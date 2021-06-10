import os
import bpy
import numpy as np
from pathlib import Path

from . import utility_fuctions
from .pattern_generator import PatternGenerator

print("########## Projector start ##########")

class Projector:
    """
    Projector class for Blender pipeline
    """

    def __init__(self, blend_camera: object, config: dict):
        print("### Projector object created ###")

        self.projector_config = config['projector']

        #Collect intrinsics from config
        self.pattern_shape = self.projector_config['resolution']
        self.focal_length = self.projector_config['focal_length']
        self.sensor_size_horizontal = self.projector_config['sensor_width']

        #Generate patterns if they dont exist
        self.pattern_generator = PatternGenerator(resolution=self.pattern_shape)
        self.patterns = self.pattern_generator.patterns_list #List of pattern dicts
        
        self.cam2proj_rot = self.projector_config['proj2cam_pose']['rotation']
        self.cam2proj_loc = self.projector_config['proj2cam_pose']['location']

        print("\n### Projector pose ###\n--> Quaternions: {}\n--> Translation: {}\n".format(self.cam2proj_rot, self.cam2proj_loc))

        self.pattern_names_list = self.pattern_generator.pattern_names
        self.pattern_filepath = Path(utility_fuctions.PathUtility.get_patterns_path())
        
        self.camera = blend_camera #BlendCamera object

        self.create_collections_and_viewlayers()
        self.import_light_sources()
        self.connect_collections_and_viewlayers()

    
    def create_collections_and_viewlayers(self):
        """
        Creates collections and viewlayers, corresponding to the generated projected patterns
        """
        
        #Set parent collection to be scene master collection
        parent_collection = bpy.context.scene.collection
        
        view_layers = bpy.context.scene.view_layers
        
        if not len(view_layers) == 1:
            raise Exception('Blender file can not contain more than one view layer when running the pipeline\nBlender file currently contains {} view layers'.format(len(view_layers)))

        bpy.context.view_layer.name = 'native_layer' #Rename native view layer

        #Seperate native lighting from projector lighting
        lights_in_scene = []
        for light in bpy.data.lights:

            if bpy.data.lights[light.name].users:
                lights_in_scene.append(light.name)

        native_lights_list = list(set(lights_in_scene) - set(self.pattern_names_list))
        
        #Create a collection to store native lighting
        native_light_collection = bpy.data.collections.new(name='native_lights')
        parent_collection.children.link(native_light_collection)

        #Add native lighting to collection
        for native_light_name in native_lights_list:

            native_light = bpy.data.objects[native_light_name]
            
            current_collection = native_light.users_collection

            #Unlink object from previous collection and link to new collection
            native_light_collection.objects.link(native_light)
            current_collection[0].objects.unlink(native_light)

        #Loop number of phase shift patterns in structured light algorithm
        for pattern_name in self.pattern_names_list:
             
            #Create viewlayers for both wave lengths at current shift
            bpy.context.scene.view_layers.new(name=pattern_name)
            
            #Create collections for both wave lengths at current shift
            collection = bpy.data.collections.new(name="{}".format(pattern_name))

            #Make collections children of master collection/scene collection
            parent_collection.children.link(collection)
        
    
    def connect_collections_and_viewlayers(self):
        """
        Connect collections with their associated view layers, to enable hiding and unhiding in other view layers.
        """

        for layer in bpy.context.scene.view_layers: #Loop layers
            native_lighting_col = bpy.context.scene.view_layers[layer.name].layer_collection.children['native_lights']

            if layer.name in self.pattern_names_list: #
                native_lighting_col.exclude = True

            for collection in bpy.context.scene.view_layers[layer.name].layer_collection.children: #Loop collections in layer

                if layer.name in self.pattern_names_list: #On a projector layer

                    if collection.name == layer.name or collection.name not in self.pattern_names_list and collection.name != 'native_lights': #Collection to show in layer
                        collection.exclude = False

                    else: #Collection not to show in layer
                        collection.exclude = True

                else: #Not a projector layer

                    if collection.name in self.pattern_names_list: #Hide the projectors in the native layers
                        collection.exclude = True
                        


    def import_light_sources(self):
        """
        Creating projector light sources in blender, and creating node tree for each pattern
        """

        print('################# importing light sources #################')
        for pattern_name in self.pattern_names_list:

            coll = bpy.data.collections[pattern_name] #Store the associated blender collection as variable

            bpy.data.lights.new(name=pattern_name, type='SPOT') #Create new light source
            
            light = bpy.data.lights[pattern_name] #Store blender light as variable
            light_obj = bpy.data.objects.new(name=pattern_name, object_data=light) #Store blender light object as variable
            coll.objects.link(light_obj) #Link light object to assiciated collection
            
            light.spot_blend = 0 #Edge blending of spotlight turned off
            light.spot_size = np.pi #Set spot field of view to 180 (Larger than the image field of view)
            light.shadow_soft_size = 0 #Makes edges of projected image sharp

            light_obj.parent = bpy.data.objects[self.camera.name] #Set light to child of camera
            light_obj.parent_type = 'OBJECT'

            light_obj.location = self.cam2proj_loc #Set light location relative to camera
            
            if len(self.cam2proj_rot) == 4:
                light_obj.rotation_mode = 'QUATERNION' #Set rotation mode to quaternion
                light_obj.rotation_quaternion = self.cam2proj_rot
            else:
                light_obj.rotation_mode = 'XYZ' #Set rotation mode to euler xyz
                light_obj.rotation_euler = self.cam2proj_rot

            light_obj.name = pattern_name #Rename light to be same as associated view layer and collection

            #Set up the node tree for the projector
            self.create_projector_node_tree(light=light)

            
    def create_projector_node_tree(self, light):
        '''
        Creates the node tree for the light source, such that it projects the pattern as a projector
        '''

        light.use_nodes = True
        node_tree = light.node_tree
        nodes = node_tree.nodes
        links = node_tree.links

        #Store auto generated nodes for later use
        emission_node = nodes[0]
        light_out_node = nodes[1]
        
        #Create and place texture coordinate node in node tree
        texture_coord_node = nodes.new(type='ShaderNodeTexCoord')
        texture_coord_node.location = (0, 0)
        texture_coord_node.name = "text_coord_{}".format(light.name)

        #Create and place separate XYZ node in node tree
        separate_xyz_node = nodes.new(type='ShaderNodeSeparateXYZ')
        separate_xyz_node.location = (200, -80)
        separate_xyz_node.name = "separateXYZ_{}".format(light.name)

        links.new(input=separate_xyz_node.inputs[0], output=texture_coord_node.outputs[1]) #Link texture node to seperate xyz node

        #Create and place vector math divide node in node tree
        divide_node = nodes.new(type='ShaderNodeVectorMath')
        divide_node.location = (400, 0)
        divide_node.operation = 'DIVIDE'
        divide_node.name = "divide_{}".format(light.name)

        links.new(input=divide_node.inputs[0], output=texture_coord_node.outputs[1]) #Link texture node divide node
        links.new(input=divide_node.inputs[1], output=separate_xyz_node.outputs[2]) #Link seperate xyz node to texture node

        #Mapping node
        mapping_node = nodes.new(type='ShaderNodeMapping')
        mapping_node.location = (600, 0)
        mapping_node.name = "mapping_{}".format(light.name)

        x_scale = (self.focal_length/(self.sensor_size_horizontal)) #Scale mapping node to focal length and vertical resolution
        y_scale = (self.focal_length/(self.sensor_size_horizontal))*(self.pattern_shape[1]/self.pattern_shape[0]) #Scale mapping node to focal length and horizontal resolution

        links.new(input=mapping_node.inputs[0], output=divide_node.outputs[0])
        mapping_node.inputs[1].default_value = [0.5,0.5,0] #Center image in sportlight
        mapping_node.inputs[2].default_value = [0,0,np.pi] #Rotate image about z-axis of camera
        mapping_node.inputs[3].default_value = [x_scale, y_scale, 1] #SCaling image mapping to fit focal length

        #Texture image node
        texture_img_node = nodes.new(type='ShaderNodeTexImage')
        texture_img_node.location = (800, 0)
        texture_img_node.name = "text_img_{}".format(light.name)

        links.new(input=texture_img_node.inputs[0], output=mapping_node.outputs[0]) #Link mapping node to texture image node
        texture_img_node.extension = 'CLIP' #Clip image, so that it doesnt repeat

        #Collect image from /utility/SL_patterns folder
        pattern_filename = '{}x{}_{}.jpg'.format(self.pattern_shape[0],self.pattern_shape[1], light.name) #Filename of pattern stored in
        pattern_img = bpy.data.images.load(filepath=str(Path.joinpath(self.pattern_filepath,Path(pattern_filename))))
        texture_img_node.image = pattern_img #Set image to be projected from node

        #Emission node
        emission_node.location = (1200, 0)
        emission_node.name = 'emission_{}'.format(light.name)

        links.new(input=emission_node.inputs[0], output=texture_img_node.outputs[0]) #Link texture image node to emission node
        emission_node.inputs[1].default_value = 5

        #Light output node
        light_out_node.location = (1400, 0)
        light_out_node.name = "light_output_{}".format(light.name)

    def get_projector_matrix(self):

        focal_length = self.focal_length
        sensor_width = self.sensor_size_horizontal

        height_px = self.pattern_shape[0]
        width_px = self.pattern_shape[1]

        pixel_width = sensor_width/width_px

        aspect_ratio = height_px/width_px

        u_0 = height_px/2
        v_0 = width_px/2

        alpha_u = focal_length*(width_px/sensor_width)
        alpha_v = focal_length*(height_px*aspect_ratio/(pixel_width*height_px))


        M = np.array([[alpha_u,       0, u_0],
                      [      0, alpha_v, v_0],
                      [      0,       0,   1]])
        return M