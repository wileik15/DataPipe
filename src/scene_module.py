import bpy
import random
from pathlib import Path
import numpy as np
import pickle

from .objects_module import ObjectManager
from .camera_module import BlendCamera

class BlendScene:

    scene_num = 0
    finished_renders = 0

    run_instance_path = ''

    def __init__(self, config: dict, camera: BlendCamera, object_manager: ObjectManager):
        self.scene_config = config['scene']

        self.object_manager = object_manager

        self.scene_number = self.get_scene_number()
        self.scene_name = "scene.{:04}".format(self.scene_num)

        print("### SCENE {} CREATED ###".format(self.scene_num))

        if self.scene_num == 1:
            self.set_run_instance_path(config=config)
        
        print("Getting run instance path")
        self.run_instance_path = self.get_run_instance_path()

        print("Getting drop zone dimensions")
        self.drop_zone_location, self.drop_zone_dimensions = self.get_drop_zone_info(scene_config=self.scene_config)
        
        print("Creating scene output path")
        self.output_path = Path.joinpath(Path(config['output']['path']), self.scene_name)
        self.output_path.mkdir()

        print("Setting boolean for scene")
        self.last_scene = False

        self.total_num_renders = self.scene_config['num_renders']

        self.renders_for_scene = self.get_num_renders(camera=camera)

        self.scene_dict = {}
    
    @classmethod
    def get_scene_number(cls):
        temp = cls.scene_num
        cls.scene_num += 1
        return cls.scene_num

    @classmethod
    def reset_scene_number(cls):
        cls.scene_num = 0

    @classmethod
    def set_run_instance_path(cls, config):
        print("Setting run instance path..")
        path = Path(config['output']['path'])
        path.mkdir()
        cls.run_instance_path = str(path)

    @classmethod
    def get_run_instance_path(cls):
        return cls.run_instance_path

    @classmethod
    def set_finished_renders(cls, renders_for_scene: int):
        cls.finished_renders += renders_for_scene

    @classmethod
    def get_num_finished_renders(cls):
        return cls.finished_renders
    
    def get_drop_zone_info(self, scene_config: dict):

        if 'drop_zone' in bpy.data.objects.keys():
            
            drop_zone_ob = bpy.data.objects['drop_zone']
            bpy.ops.object.select_all(action='DESELECT')
            drop_zone_ob.select_get()
            bpy.ops.object.transform_apply(location=False, scale=True, rotation=False)
            scale = drop_zone_ob.scale
            drop_zone_loc = drop_zone_ob.location
            drop_zone_dim = drop_zone_ob.dimensions
            
            bpy.data.objects.remove(drop_zone_ob, do_unlink=True)
            bpy.data.meshes.remove(bpy.data.meshes['drop_zone_mesh'], do_unlink=True)

        else:
            drop_zone_loc = list(scene_config['drop_zone_loc'])
            scale = scene_config['drop_zone_scale']
            drop_zone_dim = [2*scale[0], 2*scale[1], 2*scale[2]]
            
        if self.scene_num == 1:
            #Add cube under dropzone, to avoid simulation cliping through
            bpy.ops.mesh.primitive_cube_add()
            cube = bpy.context.active_object
            old_col = cube.users_collection[0]
            self.object_manager.objects_collection.objects.link(cube)
            old_col.objects.unlink(cube)

            bpy.data.meshes[cube.name].name = 'occlusion_box'
            cube.name = 'occlusion_box'
            bpy.ops.rigidbody.object_add(type='PASSIVE')
            cube_scale = [scale[0],scale[1], 0.1]

            cube.hide_render = True
            cube.scale = cube_scale
            
            cube.location = [drop_zone_loc[0], drop_zone_loc[1], drop_zone_loc[2] - drop_zone_dim[2]/2 - 0.1]
            cube.rigid_body.collision_margin = 0.001

        return list(drop_zone_loc), list(drop_zone_dim)
        

    def get_num_renders(self, camera: object):

        max_renders = self.scene_config['max_renders_per_scene']
        min_renders = self.scene_config['min_renders_per_scene']

        if max_renders > len(camera.pose_list):
            max_renders = len(camera.pose_list)

        num_renders = random.randint(a=min_renders, b=max_renders)
        finished_renders = self.get_num_finished_renders()

        if finished_renders + num_renders >= self.total_num_renders:
            num_renders = self.total_num_renders - finished_renders

            self.last_scene = True
        
        self.set_finished_renders(num_renders)
        
        return num_renders

    def write_output_info_to_scene_dict(self, render_num: int, camera: BlendCamera, object_manager: ObjectManager):
        print("\nWriting to output dict:\n")
        object_output_list = object_manager.get_objects_information_dict(camera=camera)
        render_key = 'render.{:04d}'.format(render_num)

        wrld2cam_pose = np.asarray(camera.blend_cam_obj.matrix_world)
        print("Camera matrix is\n{}".format(wrld2cam_pose))

        print("Scene dict:\n{}\n".format(self.scene_dict))
        
        self.scene_dict[render_key] = {'wrld2cam_pose': wrld2cam_pose,
                                       'objects_in_scene':object_output_list}
        print("Scene dict:\n{}\n".format(self.scene_dict))
    
    def write_scene_dict_to_file(self):

        filename = Path('output_dict.pickle')
        output_path = Path(self.run_instance_path)

        pickle_path = Path.joinpath(output_path, filename)

        if pickle_path.exists():
            path_str = str(pickle_path)
            with open(path_str, "rb") as pickle_file:
                
                info_dict = pickle.load(pickle_file)

                info_dict[self.scene_name] = self.scene_dict
            
            with open(path_str, "wb") as pickle_file_out:

                print("info dict adding to pickle file:\n{}".format(info_dict))

                pickle.dump(info_dict, pickle_file_out)
        else:
            path_str = str(pickle_path)
            with open(path_str, "wb") as pickle_file_out:
                info_dict = {self.scene_name: self.scene_dict}

                print("info dict adding to pickle file:\n{}".format(info_dict))
                
                pickle.dump(info_dict, pickle_file_out)