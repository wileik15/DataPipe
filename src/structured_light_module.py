import numpy as np
from pathlib import Path
import copy
import cv2

from .render_module import Renderer
from .pattern_generator import PatternGenerator

class Algorithm:

    def __init__(self, renderer: Renderer, pattern_names: list, pattern_generator: PatternGenerator):

        self.render_path = renderer.render_path

        self.file_paths = self.get_render_out_subdirs(pattern_names=pattern_names)

        self.images = self.load_images(file_paths=self.file_paths)

        self.periods = pattern_generator.periods

        self.phase1_img = self.phase_detection(images=self.images[:,:,:3])
        self.phase2_img = self.phase_detection(images=self.images[:,:,3:])

    
    def get_render_out_subdirs(self, pattern_names: list):
        '''
        Collects the rendered output image paths form every rendered camera angle
        '''

        render_dir = Path(self.render_path)

        file_paths = []
        print('\nFrom algorithm:')
        print("Render dir:\n{}\n".format(render_dir))

        for pattern_name in pattern_names:
            sub_dir = Path(pattern_name)
            img_dir = Path.joinpath(render_dir,sub_dir)

            for file_path in img_dir.iterdir():
                print("Iter dir Path:\n{}".format(file_path))
                print("Suffix: {}".format(file_path.suffix))
                if file_path.suffix == '.png':
                    print("-Filepath accepted.\n")
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

        print("Importing the images:\n{}".format(file_paths))
        
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
        
        #Removing noise from unlit areas
        error_img = copy.copy(out)
        error_img = np.sum(error_img**2, axis=2)
        filter_img = np.ones_like(out[:,:,0])
        filter_img[np.where(error_img < threshold)] = None
        print("\n-----out.shape: {}\n-----filter_img.shape: {}\n".format(out.shape, filter_img.shape))
        for i in range(len(out[0,0,:])):
            out[:,:,i] = np.multiply(out[:,:,i], filter_img)
            

            ####### REMOVE #######
            self.temp_save_image_to_render_path(image=out[:,:,i])
        
        return  out
    

    def phase_detection(self, images):
        '''
        Extracts the phase iamge for every shifted fringe image pattern
        '''
        print("### PHASE DETECTION ###")
        dim = images.shape

        print("Images shape: {}".format(images.shape))

        r = dim[0]
        c = dim[1]
        
        print("r: {}, c = {}".format(r,c))
        
        phase = np.empty((r,c))

        num_phase_steps = dim[2]

        ph = 2*np.pi*np.arange(0,num_phase_steps)/num_phase_steps #Plasser faseforskyningen i en vektor
        print(ph)

        sinph = np.sin(ph) #Faseforskyvningen
        cosph = np.cos(ph) #Faseforskyvningen
        print(sinph)
        print(cosph)

        print("Høyde gange bredde av bildet er: {}".format(r*c))

        image_vector = np.array(images).reshape(r*c, num_phase_steps) #Omform bildet til en vektor
        print(image_vector.shape)

        numerator = np.matmul(image_vector, sinph) #Multipliser med faseforskyvningen
        denominator = np.matmul(image_vector, cosph) #Multipliser med faseforskyvningen

        print(numerator.shape)

        phase = -np.arctan2(numerator, denominator) #Finn vinkelen i sin og cos

        phase = phase.reshape(r,c) #Form bildet tilbake til originalt format
        phase = np.mod(phase,2*np.pi) #Map verdiene til 0 til 2pi

        


        ####### REMOVE #######
        phase_temp = phase*(255/(np.pi*2))
        self.temp_save_image_to_render_path(image=phase_temp)
        
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

        abs_phase_img = abs_phase*(255/(2*np.pi))

        self.temp_save_image_to_render_path(abs_phase_img)

        return abs_phase
    

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