print("########## script start ##########")
'''
import sys
import os
sys.path.append(os.path.expanduser("~/Users/william/Documents/masters_thesis/DataPipe"))
print(sys.path)
'''
import bpy
import time
'''
from pattern_generator import PatternGenerator
from scene_module import BlendScene
'''


class Projector:

    def __init__(self):

        self.num_patterns = 2
        self.num_phase_shifts = 3
        self.pattern_shape = [1080, 1920]
        self.pattern_names_list = self.generate_pattern_names()

        #PatternGenerator.generate_fringe_patterns(self.pattern_shape[0], self.pattern_shape[1])

        self.create_collections_and_viewlayers()
        self.connect_collections_to_viewlayers()

    def generate_pattern_names(self):

        names = []

        for pattern_num in range(self.num_patterns): #Loop number of patterns

            for shift_num in range(self.num_phase_shifts): #Loop number of shifts for each pattern
                
                name = "p{}s{}".format(pattern_num+1, shift_num+1) #Create name for pattern

                names.append(name) #Store name in list 
        return names

    
    def create_collections_and_viewlayers(self):
        """
        sdads
        """

        #Set parent collection to be scene master collection
        parent = bpy.context.scene.collection

        #Loop number of phase shifts in structured light algorithm
        for pattern_name in self.pattern_names_list:
             
            #Create viewlayers for both wave lengths at current shift
            bpy.context.scene.view_layers.new(name=pattern_name)
            
            #Create collections for both wave lengths at current shift
            collection = bpy.data.collections.new(name="{}".format(pattern_name))

            #Make collections children of master collection/scene collection
            parent.children.link(collection)
        
        
        layer = bpy.context.scene.view_layers['p1s1']
        col = bpy.data.collections['p1s1']
    
    def connect_collections_to_viewlayers(self):

        start_time = time.time()

        for layer_name in self.pattern_names_list:

            for colection in bpy.context.scene.view_layers[layer_name].layer_collection.children:

                if colection.name == layer_name:

                    colection.exclude = False
                else:

                    colection.exclude = True

        end_time = time.time()

        print("Total looping time is {}".format(end_time-start_time))
    



if __name__ == '__main__':

    print("-----> Now it is main, and inside Projector class")
    
    projector = Projector()
    