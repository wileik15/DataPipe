import numpy as np
from pathlib import Path
import copy
import cv2

from .render_module import Renderer
from .pattern_generator import PatternGenerator
from .camera_module import BlendCamera

class Algorithm:

    def __init__(self, renderer: Renderer, pattern_names: list, pattern_generator: PatternGenerator, camera: BlendCamera):

        self.render_path = renderer.render_path

        self.file_paths = self.get_render_out_subdirs(pattern_names=pattern_names)

        self.images = self.load_images(file_paths=self.file_paths)

        self.periods = pattern_generator.periods

        self.phase1_img = self.phase_detection(images=self.images[:,:,:3])
        self.phase2_img = self.phase_detection(images=self.images[:,:,3:])

        self.abs_phase_img = self.absolute_phase(self.phase1_img, self.phase2_img)

        self.camera_matrix = np.matmul(camera.K, camera.camera_extrinsic)
        self.projector_matrix = np.matmul(camera.projector_matrix, camera.projector_extrinsic)

        self.depth_img, image = self.triangulate_depth(camera.projector.pattern_shape[1], 
                                                       self.abs_phase_img, 
                                                       self.camera_matrix, 
                                                       self.projector_matrix)
    
    def get_render_out_subdirs(self, pattern_names: list):
        '''
        Collects the rendered output image paths form every rendered camera angle
        '''

        render_dir = Path(self.render_path)

        file_paths = []

        for pattern_name in pattern_names:
            sub_dir = Path(pattern_name)
            img_dir = Path.joinpath(render_dir,sub_dir)

            for file_path in img_dir.iterdir():
                
                if file_path.suffix == '.png':
                    
                    file_paths.append(str(file_path))
                    break

        return file_paths

    def load_images(self,file_paths):
        '''
        Load all rendered structured light images in to matrix
        '''
        print("### LOADING IMAGES ###")
    
        supported_filetypes = ['.png', '.jpg']
        
        num_images = len(file_paths)

        threshold = (25**2)*num_images
        
        count = 0
        
        for image_path in file_paths:
            
            image_path = Path(image_path)

            if image_path.suffix not in supported_filetypes:
                raise Exception("Filetype {} not valid, use {}".format(image_path.suffix, supported_filetypes))
            
            img = cv2.imread(str(image_path))
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            (height,width) = img_gray.shape
            
            if count == 0:
                out = np.empty((height, width, num_images))
            
            out[:,:,count] = img_gray
            
            count += 1
        
        #Remove unlit noisy pixels
        error_img = copy.copy(out)
        error_img = np.sum(error_img**2, axis=2)
        filter_img = np.ones_like(out[:,:,0])
        filter_img[np.where(error_img < threshold)] = None
        
        for i in range(len(out[0,0,:])):
            out[:,:,i] = np.multiply(out[:,:,i], filter_img)
        
        return  out
    
    def remove_unlit_pixels(self, images, threshold):
        error_img = copy.copy(images)
        error_img = np.sum(error_img**2, axis=2)
        filter_img = np.ones_like(images[:,:,0])
        filter_img[np.where(error_img < threshold)] = None

        for i in range(len(images[0,0,:])):
            images[:,:,i] = np.multiply(images[:,:,i], filter_img)
        
        return images
    

    def phase_detection(self, images):
        '''
        Extracts the phase iamge for every shifted fringe image pattern
        '''
        print("### PHASE DETECTION ###")
        dim = images.shape

        r = dim[0]
        c = dim[1]
        
        phase = np.empty((r,c))
        num_phase_steps = dim[2]

        ph = 2*np.pi*np.arange(0,num_phase_steps)/num_phase_steps #Plasser faseforskyningen i en vektor
        print(ph)

        sinph = np.sin(ph) #Faseforskyvningen
        cosph = np.cos(ph) #Faseforskyvningen
        print(sinph)
        print(cosph)

        image_vector = np.array(images).reshape(r*c, num_phase_steps) #Omform bildet til en vektor
        print(image_vector.shape)

        numerator = np.matmul(image_vector, sinph) #Multipliser med faseforskyvningen
        denominator = np.matmul(image_vector, cosph) #Multipliser med faseforskyvningen

        print(numerator.shape)

        phase = -np.arctan2(numerator, denominator) #Finn vinkelen i sin og cos

        phase = phase.reshape(r,c) #Form bildet tilbake til originalt format
        phase = np.mod(phase,2*np.pi) #Map verdiene til 0 til 2pi
        
        return phase

    def absolute_phase(self, phase1, phase2):
        """
        Computes the absolute phase using two wave heterodyne principle with synthetic phase as aid.
        return param: abs_phase
        return type: numpy.ndarray
        """

        phase_eq = np.mod(phase1-phase2, np.pi*2)

        l_1 = phase1.shape[1]/self.periods[0] #Wavelength for pattern 1
        l_2 = phase1.shape[1]/self.periods[1] #Wavelength for pattern 2
        l_eq = l_2*l_1/(l_2-l_1)

        k = np.round(((l_eq/l_1) * phase_eq - phase1)/(np.pi*2))

        temp = phase1 + k * 2*np.pi

        abs_phase = temp/self.periods[0]

        return abs_phase
    


    def triangulate_depth(self, projector_res_width, abs_phase, camera_matrix, projector_matrix):
        
        P_c = camera_matrix
        P_p = projector_matrix

        depth_img = np.empty_like(abs_phase)
        count = 0

        for u_c in range(len(depth_img[:,0])):

            for v_c in range(len(depth_img[0,:])):

                phase = abs_phase[u_c,v_c]
                
                if phase is not None or phase is not 'nan':

                    v_p = projector_res_width*(phase/(np.pi*2))

                    M = np.array([[P_c[0,0] - P_c[2,0]*u_c, P_c[0,1] - P_c[2,1]*u_c, P_c[0,2] - P_c[2,2]*u_c],
                                [P_c[1,0] - P_c[2,0]*v_c, P_c[1,1] - P_c[2,1]*v_c, P_c[1,2] - P_c[2,2]*v_c],
                                [P_p[1,0] - P_p[2,0]*v_p, P_p[1,1] - P_p[2,1]*v_p, P_p[1,2] - P_p[2,2]*v_p]])
                    
                    vec = np.array([[P_c[0,3] - P_c[2,3]*u_c],
                                    [P_c[1,3] - P_c[2,3]*v_c],
                                    [P_p[1,3] - P_p[2,3]*v_p]])

                    world_coordinates = np.matmul(np.linalg.inv(M), vec)

                    depth_img[u_c,v_c] = world_coordinates[2]
                count += 1
        
        return depth_img


            

    ####### REMOVE #######
    def temp_save_image_to_render_path(self, image):
        path = Path.joinpath(Path(self.render_path), Path('image.png'))
        count = 1
        while path.exists():
            
            name = Path('image{}.png'.format(count))
            path = Path.joinpath(Path(self.render_path), name)

            count += 1

        path = str(path)
        cv2.imwrite(path, image)