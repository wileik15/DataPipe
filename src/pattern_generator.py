import os
from pathlib import Path
import cv2
import numpy as np
from numpy import pi
import copy

from . import utility_fuctions



class PatternGenerator:
    """
    Class for generating structured light patterns.
    """

    shifts = 3

    def __init__(self, resolution: list):

        self.resolution = np.asarray(resolution)

        self.num_phase_shifts = 3
        self.periods = [10, 9]

        self.patterns_list = []
        self.generate_fringe_pattern(resolution=self.resolution, periods=self.periods[0])
        self.generate_fringe_pattern(resolution=self.resolution, periods=self.periods[1])

        self.store_patterns()

        self.pattern_names = self.get_pattern_names_list()


    def get_pattern_names_list(self):
        """
        Generate a list of pattern names to be used in creation of viewlayers
        """

        names = []

        for pattern in self.patterns_list:
            names.append(pattern['name'])
        return names


    def generate_fringe_pattern(self, resolution: list, periods: int):
        """
        Generates three monochrome fringe patterns for structured light scanner

        :param width: image width
        :type width: int
        :param height: image height
        :type height: int
        :param periods: number of full periods along image width
        :type periods: int.
        """
        print("..... Generating patterns")

        resolution = np.asarray(resolution)
        print("Resolution: {}".format(resolution))
        height, width = resolution[0], resolution[1]
            
        periods = periods
        shifts = self.num_phase_shifts

        print("Image width: {}\nPeriods: {}\nShifts: {}".format(width,periods,shifts))
        
        delta_x= round(2*pi*periods/(width),ndigits=7) 
        x = np.arange(0,2*pi*periods-delta_x,delta_x)
        print("elements of x:\nFirst: {}\nLast: 2*pi*{}".format(x[0],x[-1]/(2*np.pi)))

        print("delta x: {}".format(delta_x))
        print("delta_x*width/2pi={}".format(delta_x*width/(np.pi*2)))
        print("X shape: {}".format(x.shape))
        
        phi = 2*pi/shifts
        
        canvas = np.ones((height,width,shifts))
        waves = np.transpose(255 * (0.6 + 0.4 * np.cos(np.array([x, x + phi, x - phi]))))
        print("Canvas shape:{}\nWaves shape: {}".format(canvas.shape,waves.shape))
        patterns = canvas*waves

        print("Canvas shape: {}".format(canvas.shape))
        print("Waves shape: {}".format(waves.shape))

        print("Shifts: {}".format(shifts))
        print("Patterns shape: {}\n-------------".format(patterns.shape))

        for shift in range(shifts):
            print("This is shift {}".format(shift))
            name = 'p{}s{}'.format(periods, shift+1)
            print("\nPattern: {}\nShape: {}\n---------------".format(name, patterns[:,:,shift].shape))
            pattern = copy.copy(patterns[:,:, shift])
            
            pattern_dict = {'name': name,
                            'pattern':pattern}

            self.patterns_list.append(pattern_dict)


    def store_patterns(self):
        """
        Stores generated pattern images in utility folder
        """

        patterns_folder_path = Path(utility_fuctions.PathUtility.get_patterns_path())

        for pattern in self.patterns_list:

            height, width = pattern['pattern'].shape

            filename = "{}x{}_{}.jpg".format(height, width, pattern['name'])

            Path(filename)
            save_path = str(Path.joinpath(patterns_folder_path, filename))

            pattern['filename'] = save_path
            
            if not os.path.exists(save_path): #Check if the pattern already exist
                cv2.imwrite(save_path, pattern['pattern'])




