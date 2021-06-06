import types
import numpy as np
from pathlib import Path
import cv2

from .render_module import Renderer

class Algorithm:

    def __init__(self, renderer: Renderer, pattern_names: list):

        self.render_path = renderer.render_path

        self.file_paths = self.get_render_out_subdirs(pattern_names=pattern_names)

    
    def get_render_out_subdirs(self, pattern_names: list):

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

    def load_images(directory, file_subdirs_list):
    
        supported_filetypes = ['.png', '.jpg']
        
        directory = Path(directory)
        
        num_images = len(file_subdirs_list)
        
        count = 0
        
        for filename in file_subdirs_list:
            
            filename = Path(filename)
            
            img_path = Path.joinpath(directory, filename)
            if img_path.suffix not in supported_filetypes:
                raise Exception("Filetype {} not valid, use {}".format(img_path.suffix, supported_filetypes))
            
            img = cv2.imread(str(img_path))
            
            (height, width, chanels) = img.shape
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            (height,width) = img_gray.shape
            
            if count == 0:
                out = np.empty((height, width, num_images))
            
            out[:,:,count] = img_gray
            
            count += 1
        
        return  out
    

