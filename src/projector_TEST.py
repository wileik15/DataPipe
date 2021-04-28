print("########## script start ##########")

import sys
import os
import random
#sys.path.append(os.path.expanduser('~Users/William/Documents/masters_thesis/DataPipe/'))
print(os.getcwd())

import bpy
import time
import numpy as np
from pathlib import Path

###########################################
################ TEMPORARY ################
###########################################

import json
import subprocess
from scipy.spatial.transform import Rotation


def quat2rot(quat):
    """
    Converts blender quaternion representation to rotation matrix

    :param: quat
    :type quat: array
    """
    #Converts from blender quaternion representation
    q = [quat[1], quat[2], quat[3], quat[0]]

    quat = Rotation.from_quat(q) #Stores as a rotation
    R = quat.as_matrix() #Rotation matrix
    return R

def rot2quat(rot):
    """
    Converts a rotation matrix to  blender quaternion representation

    :param: rot
    :type rot: array
    """
    R = Rotation.from_matrix(rot) #Stores as a rotation
    q = R.as_quat() #Quaternions

    quat = [q[3], q[0], q[1], q[2]] #Saves quaternion in Blender representation
    return quat


def pose_to_tranformation_matrix(quaternions, location):
    """
    Changes Blenders quaternion representation and location
    to transformation matrix representation
    """
    R = quat2rot(quat=quaternions)
    t = location

    T = np.array([[R[0,0], R[0,1], R[0,2], t[0]],
                    [R[1,0], R[1,1], R[1,2], t[1]],
                    [R[2,0], R[2,1], R[2,2], t[2]],
                    [0,      0,      0,      1   ]])
    return T, R, t


def transformation_matrix_to_quat_and_translation(matrix):
    """
    Converts pose from transformation matrix format to quaternions and translation

    return: [quaternions] and [x,y,z]
    """
    quat = rot2quat(rot=matrix[0:3,0:3])
    trans = [matrix[0,3], matrix[1,3], matrix[2,3]]
    return quat, trans


def transform_inverse(matrix):
    R = matrix[0:3, 0:3]
    t = matrix[0:3, 3]

    T = np.zeros_like(matrix)
    T[0:3, 0:3] = np.transpose(R)
    T[0:3, 3] = - np.transpose(R)@t
    T[3,3] = 1
    return T


def cam2obj_transform(blender_object, cam_pos_matrix):
    obj_translation = blender_object.location #Get object location vector
    obj_quaternions = blender_object.rotation_quaternion #Get object rotation on quaternion
    obj_trans_quaternions = rot2quat(quat2rot(obj_quaternions))

    cam_translation = cam_pos_matrix[0:3,3] #Get camera location vector
    cam_quaternions = rot2quat(cam_pos_matrix[0:3,0:3]) #Get camera rotation on quaternion

    T_so, R_so, t_so = pose_to_tranformation_matrix(obj_quaternions, obj_translation) #Object transformation matrix in world coordinates
    T_sc, R_sc, t_sc = pose_to_tranformation_matrix(cam_quaternions, cam_translation) #Camera transformation matrix in world coordinates

    T_cs = transform_inverse(T_sc) #World coordinate system in camera coordinate system

    T_co = np.matmul(T_cs,T_so) #Object transform from camera coordinate system
    R_co = T_co[0:3,0:3] #Rotation
    t_co = T_co[0:3,3] #Translation

    return T_co, R_co, t_co

#############################################
############## Projector Class ##############
#############################################

class Projector:
    """
    Projector class for Blender
    """

    def __init__(self, blend_camera: object, config: dict):

        self.num_patterns = 2
        self.num_phase_shifts = 3
        self.pattern_shape = [1080, 1920] # This should be collected from config file
        self.focal_length = 50            # This should be collected from config file
        self.sensor_size_horizontal = 36  # This should be collected from config file
        
        self.proj2cam_rotation_quat, self.proj2cam_translation = transformation_matrix_to_quat_and_translation(config["projector"]["proj2cam_pose"])
        print(self.proj2cam_rotation_quat, self.proj2cam_translation)
        self.pattern_names_list = self.generate_pattern_names()
        self.pattern_filepath = '/Users/william/Documents/masters_thesis/DataPipe/utility/SL_patterns/'
        
        self.camera = blend_camera #BlendCamera object

        #PatternGenerator.generate_fringe_patterns(self.pattern_shape[0], self.pattern_shape[1])

        print(bpy.data.scenes['Scene'].collection)

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
            print("Light {} is used: {}".format(light.name,bpy.data.lights[light.name].users))
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

            light_obj.location = self.proj2cam_translation #Set light location relative to camera
            light_obj.rotation_quaternion = self.proj2cam_rotation_quat

            light_obj.name = pattern_name #Rename light to be same as associated view layer and collection
            
            #def create_projector_node_tree(self, light)
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

            pattern_filename = '{}x{}_{}.jpg'.format(self.pattern_shape[0],self.pattern_shape[1], light.name) #Filename of pattern stored in
            pattern_img = bpy.data.images.load(filepath=os.path.join(self.pattern_filepath,pattern_filename))
            texture_img_node.image = pattern_img

            
            emission_node.location = (1200, 0)
            emission_node.name = 'emission_{}'.format(light.name)

            links.new(input=emission_node.inputs[0], output=texture_img_node.outputs[0]) #Link texture image node to emission node
            emission_node.inputs[1].default_value = 10

            light_out_node.location = (1400, 0)
            light_out_node.name = "light_output_{}".format(light.name)


##########################################
############## Camera Class ##############
##########################################

class BlendCamera:

    def __init__(self, camera_name: str, config: dict):

        self.name = camera_name
        self.is_structured_light = config["camera"]["is_structured_light"]

        self.pose_list = config["camera"]["wrld2cam_pose_list"]

        blend_cam_obj = self.import_camera()

        if self.is_structured_light:
            projector = Projector(self, config=config)
        


    def import_camera(self):

        camera = bpy.data.cameras.new(name=self.name)
        camera_obj = bpy.data.objects.new(name=self.name, object_data=camera)
        
        parent_col = bpy.context.scene.collection
        parent_col.objects.link(camera_obj)


        #Move to first pose
        self.move(camera_obj)

        return camera_obj
        


    def get_random_pose_from_list(self):
        
        poses = self.pose_list

        #Pick random index of pose list
        index = random.randint(a=0, b=len(poses)-1)
        print("Camera random pos: {}".format(poses[index]))

        return poses[index]
    
    def move(self, blend_obj):
        #Sample random pose from input list
        rand_pose = self.get_random_pose_from_list()
        rot_quat, transl = transformation_matrix_to_quat_and_translation(rand_pose)
        print("Blender object: {}".format(blend_obj.name))
        print("Rotation = {}\nTranslation = {}".format(rot_quat, transl))
        #Set blender camera objects position
        blend_obj.rotation_quaternion = rot_quat
        blend_obj.location = transl




if __name__ == '__main__':

    start_time = time.time()

    config_dict = {"camera": {"wrld2cam_pose_list": [np.array([[0.7071068, -0.7071068,  0.0000000, 0],
                                                [0.0000000, -0.0000000, -1.0000000, 0],
                                                [0.7071068,  0.7071068,  0.0000000, 0.5],
                                                [0, 0, 0, 1]])],
                              "is_structured_light": True
                             },
                  "projector": {"proj2cam_pose": np.array([[0.9890159,  0.0000000, -0.1478094, -0.15],
                                                            [0.0000000,  1.0000000,  0.0000000, 0],
                                                            [0.1478094,  0.0000000,  0.9890159, 0],
                                                            [0, 0, 0, 1]])
                                 
                                }
                  }

    #BlendScene.set_up_scene()
    cam = BlendCamera(camera_name= 'Cam', config=config_dict)

    end_time = time.time()

    print("\n#############################\n# Total runtime is: {:.4f}s #\n#############################\n".format(end_time - start_time))
    
print("######### SCRIPT ENDED #########")


###########################################
################ TEMPORARY ################
###########################################


class VersionControll:

    @staticmethod
    def blenderVersionCheck():
        """
        Verifies that Blender version 2.80 or later is installed
        """

        version = (bpy.app.version_string).split('.')

        if not (int(version[1]) >= 90):
            raise Exception("Blender version 2.80 or newer required.\n- Current version is Blender {}.{}.{}".format(version[0],version[1],version[2]))



class PackageControll:

    @staticmethod
    def installDependencies(package_list):
        """
        installing package dependencies to Blenders bundled python
        """

        #Path to python executable
        py_exec = str(bpy.app.binary_path_python)

        #Ensure that pip is installed
        subprocess.call([py_exec, '-m', 'ensurepip', '--user'])

        #Install latest version of pip
        subprocess.call([py_exec, '-m', 'pip', 'install', '--upgrade', 'pip'])

        #Loop package list to install all of them
        for package_name in package_list:
            subprocess.check_call([py_exec, '-m', 'pip', 'install','{}'.format(package_name)])
