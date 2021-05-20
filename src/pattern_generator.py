import os
from pathlib import Path
import cv2
import numpy as np
from numpy import pi
from . import utility_fuctions



class PatternGenerator:
    """
    Class for generating structured light patterns.
    """

    shifts = 3

    @classmethod
    def generate_fringe_patterns(cls, resolution):
        """
        Generates three monochrome fringe patterns for structured light scanner

        :param width: image width
        :type width: int
        :param height: image height
        :type height: int
        :param periods: number of full periods along image width
        :type periods: int.
        """
        print("..... Generating patterns, please hold wait")

        height = resolution[0]
        width = resolution[1]

        if not cls.pattern_exists(height, width):
            
            periods1, periods2 = 8, 7
            shifts = cls.shifts
            
            delta_x1, delta_x2 = 2*pi*periods1/width, 2*pi*periods2/width
            x_1, x_2 = np.arange(0,2*pi*periods1,delta_x1), np.arange(0,2*pi*periods2,delta_x2)
            
            phi = 2*pi/shifts
            
            canvas = np.ones((height,width,shifts*2))
            waves = np.transpose(255 * (0.6 + 0.4 * np.cos(np.array([x_1, x_1 + phi, x_1 - phi, x_2, x_2 + phi, x_2 - phi]))))
            patterns = canvas*waves

            cls.store_patterns(patterns)
    
    
    @staticmethod
    def store_patterns(patterns):
        """
        Stores generated pattern images in utility folder

        :param patterns: matrix containing all patterns
        :type patterns: numpy.ndarray
        """

        height, width = len(patterns[:,0,0]), len(patterns[0,:,0])
        shift = 1

        patterns_folder_path = utility_fuctions.PathUtility.get_patterns_path()

        for i in range(0,int(len(patterns[0,0,:])/2)):
            filename1 = "{}x{}_p1s{}.jpg".format(height, width, shift)
            filename2 = "{}x{}_p2s{}.jpg".format(height, width, shift)
            
            cv2.imwrite("{}{}".format(patterns_folder_path, filename1), patterns[:,:,i])
            cv2.imwrite("{}{}".format(patterns_folder_path, filename2), patterns[:,:,i+3])
            
            shift += 1


    @staticmethod
    def pattern_exists(height, width):
        """
        Checks for existing patterns of same resolution,
        returns bool.

        :param height: Height of pattern image in pixels
        :type height: int
        :param width: Width of pattern image in pixels
        :type width: int
        """
        patterns_folder_path = utility_fuctions.PathUtility.get_patterns_path()
        
        path = Path("{}{}x{}_p1s1.jpg".format(patterns_folder_path, height, width))
        print("\n# Pattern file path checked for existence:\n{}\n".format(path.name))

        return os.path.exists(path.name)



