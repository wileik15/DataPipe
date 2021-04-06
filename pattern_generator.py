import cv2
import numpy as np


class PatternGenerator:

    
    def generate_patterns(width, height, periods):
        """
        Generates three monochrome fringe patterns for structured light scanner

        :param width: image width
        :type width: int
        :param height: image height
        :type height: int
        :param periods: number of full periods along image width
        :type periods: int
        """
    
        pi = np.pi
        
        im1, im2, im3 = np.ones((height,width)), np.ones((height,width)), np.ones((height,width))
        
        delta_x = 2*pi*periods/width
        x = np.arange(0,2*pi*periods,delta_x)
        
        phi = 2*pi/3
        
        w1, w2, w3 = 255*(0.6 + 0.4*np.cos(x)), 255*(0.6 + 0.4*np.cos(x + phi)), 255*(0.6 + 0.4*np.cos(x - phi))
        im1, im2, im3 = im1*w1, im2*w2, im3*w3
        
        return im1, im2, im3