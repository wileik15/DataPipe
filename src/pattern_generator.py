import cv2
import numpy as np
from pathlib import Path
from numpy import pi


class patternGenerator:

    @staticmethod
    def generate_fringe_patterns(width, height):
        """
        Generates three monochrome fringe patterns for structured light scanner

        :param width: image width
        :type width: int
        :param height: image height
        :type height: int
        :param periods: number of full periods along image width
        :type periods: int
        """

        periods1, periods2 = 8, 7
        shifts = 3
        
        canvas = np.ones((height,width,shifts*2))
        
        delta_x1, delta_x2 = 2*pi*periods1/width, 2*pi*periods2/width
        x1, x2 = np.arange(0,2*pi*periods1,delta_x1), np.arange(0,2*pi*periods2,delta_x2)
        
        phi = 2*pi/shifts
        
        waves = np.transpose(255 * (0.6 + 0.4 * np.cos(np.array([x1, x1 + phi, x1 - phi, x2, x2 + phi, x2 - phi]))))
        return canvas*waves
    
    @staticmethod
    def store_patterns(patterns):
        """
        Stores generated pattern images in utility folder

        :param patterns: matrix containing all patterns
        :type patterns: numpy.ndarray
        """

        height, width = patterns[:,0,0], patterns[0,:,0]

        for i in range(0,patterns[0,0,:]/2,2):
            filename1 = "{}x{}_p1s{}".format(height, width, i+1)
            filename2 = "{}x{}_p2s{}".format(height, width, i+1)

            cv2.imwrite("")

    @staticmethod
    def pattern_exists(height, width):

        return True


if __name__ == '__main__':

    patternGenerator.generate_fringe_patterns(1920, 1080)