import types
import bpy
import os
import numpy as np
import random
import copy

from .camera_module import BlendCamera


class BlendObject:

    def __init__(self, object_info: dict, index: int, collection):
        
        #Collect input data
        self.filepath = object_info['filepath']
        self.scale = object_info['scale']
        self.mass = object_info['mass']
        self.collision_shape = object_info['collision_shape']
        self.index = index

        #Set unique pbject name and add to collection
        self.name = 'DataPipe_object.{:04d}'.format(self.index) #Set object name
        self.objects_collection = collection

        print("### OBJECT {} CREATED".format(self.name))

        #Import object to blender
        filename, blend_ob, blend_mat, blend_mesh = self.import_ob(filepath=self.filepath, index=self.index, scale=self.scale)
        self.filename = filename
        self.blend_ob = blend_ob
        self.blend_mat = blend_mat
        self.blend_mesh = blend_mesh

        self.dimensions = self.get_object_dimensions()

    
    def import_ob(self, filepath: str, index: int, scale: float):
        
        head, tail = os.path.split(filepath)
        filename = tail.replace('.obj', '') #Extract filename

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.import_scene.obj(filepath=str(filepath))

        obj_in_file = len(bpy.context.selected_objects)
        if obj_in_file != 1: #Can only contain one object.
            raise Exception(".obj file can not contain more than one object, there are {} objects in file:\n{}".format(obj_in_file, filepath))
        
        if bpy.context.selected_objects[0].name != filename:
            filename = bpy.context.selected_objects[0].name
        
        obj = bpy.data.objects[filename]
        mat = obj.active_material
        mesh = bpy.data.meshes[filename]

        #Set names to current object name
        obj.name = self.name
        mat.name = self.name
        mesh.name = self.name

        #Remove from default collection and add to datapipe object collection
        obj.users_collection[0].objects.unlink(obj)
        self.objects_collection.objects.link(obj)

        #Apply object scaling
        obj.scale = (scale, scale, scale) #Set scale from user input
        bpy.ops.object.transform_apply(location=False, scale=True, rotation=False) #Apply scale to object
        
        #Set object physics properties
        bpy.context.view_layer.objects.active = obj
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        bpy.context.object.rigid_body.collision_shape = self.collision_shape 
        obj.rigid_body.mass = self.mass
        obj.rigid_body.collision_margin = 0.001

        obj.pass_index = index #Set pass index for masked image

        return filename, obj, mat, mesh
    
    def get_object_dimensions(self):

        return self.blend_ob.dimensions

    def delete_ob(self):
        print("Blender object {} deleted".format(self.name))

        bpy.data.objects.remove(self.blend_ob, do_unlink=True)
        bpy.data.materials.remove(self.blend_mat, do_unlink=True)
        bpy.data.meshes.remove(self.blend_mesh, do_unlink=True)

    def place_ob(self, x, y, z):
        
        self.blend_ob.location = x, y, z
        self.blend_ob.rotation_mode = 'XYZ'
        self.blend_ob.rotation_euler = (random.random()*2*np.pi, random.random()*2*np.pi, random.random()*2*np.pi)
        


class ObjectManager:

    def __init__(self, config: dict):
        
        self.objects_config = config['objects'] #Collect input dict

        self.objects_info_list = self.objects_config['objects_list'] #Object info list
        self.objects_in_scene = []

        self.objects_collection = self.create_objects_collection() #Create collection to store pipeline objects


    def create_objects_collection(self):

        objects_collection = bpy.data.collections.new('DataPipe_objects')
        bpy.context.scene.collection.children.link(objects_collection)

        return objects_collection

    def import_objects(self):

        self.delete_all_objects()

        index = 1
        print("\n### Importing objects ###\n")
        for object_input in self.objects_info_list:

            max_instances = object_input['max']
            min_instances = object_input['min']

            instances_in_scene = random.randint(a=min_instances, b=max_instances)

            for instance in range(instances_in_scene):

                obj = BlendObject(object_info=object_input, index=index, collection=self.objects_collection)

                self.objects_in_scene.append(obj)

                index += 1
        random.shuffle(self.objects_in_scene) #Randomizing the order of the objects

    def delete_all_objects(self):
        if len(self.objects_in_scene) != 0:
            
            for obj in self.objects_in_scene:
                obj.delete_ob()

                del obj

            self.objects_in_scene = []

    def create_initial_positions(self, scene):

        drop_zone_loc = scene.drop_zone_location
        drop_zone_dim = scene.drop_zone_dimensions

        z = drop_zone_loc[2] #Set initial z-coordinate to be at the midpoint of the dropzone height
        delta_z = 0

        max_x_coord = drop_zone_loc[0] + drop_zone_dim[0]/2 #Max x-value to place objects
        min_x_coord = drop_zone_loc[0] - drop_zone_dim[0]/2 #Min x-value to place objects

        max_y_coord = drop_zone_loc[1] + drop_zone_dim[1]/2 #Max y-value to place objects
        min_y_coord = drop_zone_loc[1] - drop_zone_dim[1]/2 #Min y-value to place objects

        for obj in self.objects_in_scene: #place objects random
            
            max_dim = max(obj.dimensions) #The object's maximal dimension (either x, y, or z direction)

            max_x_obj = max_x_coord - max_dim/2
            min_x_obj = min_x_coord + max_dim/2

            max_y_obj = max_y_coord - max_dim/2
            min_y_obj = min_y_coord + max_dim/2

            x = random.random()*(max_x_obj-min_x_obj) + min_x_obj
            y = random.random()*(max_y_obj-min_y_obj) + min_y_obj

            z += delta_z + max_dim/2

            obj.place_ob(x=x, y=y, z=z)

            delta_z = max_dim/2
    
    def get_objects_information_dict(self, camera: BlendCamera):

        obj_output_list = []

        for obj in self.objects_in_scene:

            dict = {}

            wrld2cam_transform = np.asarray(camera.blend_cam_obj.matrix_world)

            wrld2obj_transform = np.asarray(obj.blend_ob.matrix_world)
            
            cam2obj_pose = np.matmul(np.linalg.inv(wrld2cam_transform), wrld2obj_transform)

            dict = {'name': obj.name,
                    'filename': obj.filename,
                    'mask_index': obj.index,
                    'cam2obj_pose': cam2obj_pose}

            obj_output_list.append(dict)


        return obj_output_list