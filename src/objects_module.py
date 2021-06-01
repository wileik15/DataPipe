import types
import bpy
import os
import numpy as np
import random
import copy

from .scene_module import BlendScene

from .config_module import input_storage


class BlendObject:

    def __init__(self, object_info: dict, index: int, collection):
        
        #Collect input data
        self.filepath = object_info['filepath']
        self.scale = object_info['scale']
        self.index = index
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
        print(f"Object {self.name} imported\n- Filename: {self.filename}\n- Scale: {self.scale}\n- Index: {self.index}\n- Dimensions: {self.dimensions}\n")
    

    
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

        #Add to remove from default collection and datapipe object collection
        obj.users_collection[0].objects.unlink(obj)
        self.objects_collection.objects.link(obj)

        obj.scale = (scale, scale, scale) #Set scale from user input
        bpy.ops.object.transform_apply(location=False, scale=True, rotation=False) #Apply scale to object
        
        bpy.context.view_layer.objects.active = obj
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        bpy.context.object.rigid_body.collision_shape = 'MESH' # 'CONVEX_HULL' #
        obj.rigid_body.mass = 2

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
        print("\n---------------------------\nImporting objects:\n")
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
        print("Deleting {} objects".format(len(self.objects_in_scene)))
        if len(self.objects_in_scene) != 0:
            
            for obj in self.objects_in_scene:
                obj.delete_ob()

                del obj

            self.objects_in_scene = []

    def create_initial_positions(self, scene: BlendScene):

        drop_zone_loc = scene.drop_zone_location
        drop_zone_dim = scene.drop_zone_dimensions

        z = drop_zone_loc[2] #Set initial z-coordinate to be at the midpoint of the dropzone height
        delta_z = 0

        max_x_coord = drop_zone_loc[0] + drop_zone_dim[0]/2 #Max x-value to place objects
        min_x_coord = drop_zone_loc[0] - drop_zone_dim[0]/2 #Min x-value to place objects

        max_y_coord = drop_zone_loc[1] + drop_zone_dim[1]/2 #Max y-value to place objects
        min_y_coord = drop_zone_loc[1] - drop_zone_dim[1]/2 #Min y-value to place objects

        print("Placing objects at \nloc: {}\nbounds: {}".format(drop_zone_loc,drop_zone_dim))
        print("Currently, objects in scene is:\n{}".format(self.objects_in_scene))

        for obj in self.objects_in_scene:
            
            max_dim = max(obj.dimensions) #The object's maximal dimension (either x, y, or z direction)

            max_x_obj = max_x_coord - max_dim/2
            min_x_obj = min_x_coord + max_dim/2

            max_y_obj = max_y_coord - max_dim/2
            min_y_obj = min_y_coord + max_dim/2

            x = random.random()*(max_x_obj-min_x_obj) + min_x_obj
            y = random.random()*(max_y_obj-min_y_obj) + min_y_obj

            z += delta_z + max_dim/2

            print("### {} pose:\n- Before: {}".format(obj.name, obj.blend_ob.location))

            obj.place_ob(x=x, y=y, z=z)

            print("- After: {}".format(obj.blend_ob.location))

            delta_z = max_dim/2
            

            print("Object {} max dimension is: {}".format(obj.name, max_dim))