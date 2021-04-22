print("########## script start ##########")

import sys
import os
sys.path.append(os.path.expanduser("~/Users/william/Documents/masters_thesis/DataPipe"))
print(sys.path)
'''
from src.pattern_generator import PatternGenerator
from src.scene_module import BlendScene
'''
import bpy
import time



class Projector:

    def __init__(self, camera_name):

        self.num_patterns = 2
        self.num_phase_shifts = 3
        self.pattern_shape = [1080, 1920]
        self.pattern_names_list = self.generate_pattern_names()
        self.camera = camera_name

        #PatternGenerator.generate_fringe_patterns(self.pattern_shape[0], self.pattern_shape[1])

        self.create_collections_and_viewlayers()
        self.import_light_sources()
        self.connect_collections_and_viewlayers()
        
        

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
        parent_collection = bpy.context.scene.collection

        #Seperate native lighting from projector lighting
        lights_in_scene = []
        for light in bpy.data.lights:
            lights_in_scene.append(light.name)

        native_lights_list = list(set(lights_in_scene) - set(self.pattern_names_list))
        
        #Create a collection to store native lighting
        native_light_collection = bpy.data.collections.new(name='native_lights')
        parent_collection.children.link(native_light_collection)

        #Add native lighting to collection
        for native_light_name in native_lights_list:
            print(f'################################\nCurrent loop, light name: {native_light_name}')

            #Link native light to camera
            native_light = bpy.context.scene.objects[native_light_name] #Light object
            print(f'- native_light\nObject: {native_light}\nName: {native_light.name}\nType: {type(native_light)}\n')
            current_collection = native_light.users_collection
            print("Native light parent: {}".format(current_collection))

            #Unlink object from previous collection and link to new collection
            native_light_collection.objects.link(native_light)
            current_collection.objects.unlink(native_light)

            print("################################")

        #Loop number of phase shift patterns in structured light algorithm
        for pattern_name in self.pattern_names_list:
             
            #Create viewlayers for both wave lengths at current shift
            bpy.context.scene.view_layers.new(name=pattern_name)
            
            #Create collections for both wave lengths at current shift
            collection = bpy.data.collections.new(name="{}".format(pattern_name))

            #Make collections children of master collection/scene collection
            parent_collection.children.link(collection)
        
    
    def connect_collections_and_viewlayers(self):

        start_time = time.time()
        print(self.pattern_names_list)

        for layer in bpy.context.scene.view_layers: #Loop layers
            print("\n##### Layer {} #####\n".format(layer.name))
            native_lighting_col = bpy.context.scene.view_layers[layer.name].layer_collection.children['native_lights']

            if layer.name in self.pattern_names_list: #
                native_lighting_col.exclude = True

            for collection in bpy.context.scene.view_layers[layer.name].layer_collection.children: #Loop collections in layer
                print("     Collection {}".format(collection.name))
                if layer.name in self.pattern_names_list: #On a projector layer
                    print("     (Layer name IS in pattern list)")

                    if collection.name == layer.name or collection.name not in self.pattern_names_list and collection.name != 'native_lights': #Collection to show in layer
                        collection.exclude = False
                        print("     --> Collection = layer, NOT hiding collection {}\n-----------".format(collection.name))

                    else: #Collection not to show in layer
                        collection.exclude = True
                        print("     --> Collection != layer, hiding collection {}\n-----------".format(collection.name))

                else: #Not a projector layer
                    print("     (Layer name is NOT in pattern list)")

                    if collection.name in self.pattern_names_list: #Hide the projectors in the native layers
                        collection.exclude = True
                        print("     --> Collection is in pattern_ list, hiding collection {}\n-----------".format(collection.name))
                    
                    else:
                        print("     --> Collection is NOT in pattern_ list, NOT hiding collection {}\n-----------".format(collection.name))

        end_time = time.time()

        print("Total looping time is {}".format(end_time-start_time))


    def import_light_sources(self):

        for pattern_name in self.pattern_names_list:

            collection = bpy.data.collections[pattern_name] #Store the associated blender collection as variable

            bpy.ops.object.light_add(type='SPOT') #Create new light source
            light_obj = bpy.context.active_object #Store blender object as variable

            light_obj.parent = bpy.data.objects[self.camera] #Set light to child of camera
            light_obj.parent_type = 'OBJECT'

            light_obj.name = pattern_name #Rename light to be same as associated view layer and collection
            
            #def create_projector_node_tree(self, light_object)
            light = bpy.data.lights[light_obj.name]
            light.use_nodes = True
            node_tree = light.node_tree

            print(list(node_tree.nodes))




            
            
            
            

            collection.objects.link(light_obj)





if __name__ == '__main__':

    print("-----> Now it is main, and inside Projector class")

    #BlendScene.set_up_scene()
    
    projector = Projector(camera_name='Camera')
    
    print("######### SCRIPT ENDED #########")