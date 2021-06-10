import pickle
from pathlib import Path
import os
from . import utility_fuctions

import bpy

class input_storage:

    config_dict = {
                    'camera': {
                        'wrld2cam_pose_list':[],
                        'focal_length': 50,
                        'sensor_width': 36,
                        'resolution': [480, 720],
                        'is_structured_light': False

                    },
                    'projector': {
                        'proj2cam_pose': {},
                        'focal_length': 50,
                        'sensor_width': 36,
                        'resolution': [480, 720]
                    },
                    'scene': {
                        'num_renders': 1,
                        'max_renders_per_scene': 1,
                        'min_renders_per_scene': 1,
                        'drop_zone_loc': [0, 0, 2],
                        'drop_zone_scale': [0.5, 0.5, 0.5]

                    },
                    'objects': {
                        'objects_list':[]

                    },
                    'output': {
                        'path': ''
                    }

    }

    @classmethod
    def reset_config_dict(cls):
        """
        Resets configuration dict for the full pipeline.
        """

        cls.config_dict = {
                            'camera': {
                                'wrld2cam_pose_list':[],
                                'focal_length': 50,
                                'sensor_width': 36,
                                'resolution': [480, 720],
                                'is_structured_light': False

                            },
                            'projector': {
                                'proj2cam_pose': {},
                                'focal_length': 50,
                                'sensor_width': 36,
                                'resolution': [480, 720]
                            },
                            'scene': {
                                'num_renders': 1,
                                'max_renders_per_scene': 1,
                                'min_renders_per_scene': 1,
                                'drop_zone_loc': [0, 0, 2],
                                'drop_zone_scale': [0.5, 0.5, 0.5]

                            },
                            'objects': {
                                'objects_list':[]

                            },
                            'output': {
                                'path': ''
                            }

            }
    
    @classmethod
    def write_to_config_dict(cls, context):

        config = cls.config_dict

        scene_config = config['scene']
        objects_config = config['objects']
        camera_config = config['camera']
        projector_config = config['projector']
        output_config = config['output']

        #Scene inputs
        scene_config['num_renders'] = context.scene.num_renders
        scene_config['max_renders_per_scene'] = context.scene.max_renders_per_scene
        scene_config['min_renders_per_scene'] = context.scene.min_renders_per_scene

        #Drop zone inputs
        drop_zone = bpy.data.objects['drop_zone'] #Get blender object

        bpy.ops.object.select_all(action='DESELECT') #Deselect all object in blender scene

        if drop_zone.select_get() is False:
            drop_zone.select_set(True) #Select dropzone object

        bpy.context.view_layer.objects.active = drop_zone #Set to active object

        bpy.ops.object.select_all(action='DESELECT') #Deselect all object after

        #Store object data in config
        scene_config['drop_zone_loc'] = list(bpy.data.objects['drop_zone'].location)
        scene_config['drop_zone_scale'] = list(bpy.data.objects['drop_zone'].scale)

        #Camera intrinsics 
        camera_config['focal_length'] = context.scene.camera_focal_length
        camera_config['sensor_width'] = context.scene.camera_sensor_width
        camera_config['resolution'] = [context.scene.camera_resolution_height, context.scene.camera_resolution_width]
        camera_config['is_structured_light'] = context.scene.is_structured_light
        
        #Projector intrinsics
        projector_config['focal_length'] = context.scene.projector_focal_length
        projector_config['sensor_width'] = context.scene.projector_sensor_width
        projector_config['resolution'] = [context.scene.projector_resolution_height, context.scene.projector_resolution_width]
        
        #Projector extrinsics
        loc = list(context.scene.projector_loc_vec)
        if context.scene.projector_rot_enum == 'quat':
            rot = list(context.scene.projector_rot_quat)
        else:
            rot = list(context.scene.projector_rot_xyz)
        
        projector_config['proj2cam_pose'] = {'rotation': rot, 'location': loc}

        #Output
        output_config['path'] = utility_fuctions.PathUtility.get_pipeline_run_output_path(context.scene.pipeline_output_path)

    
    @classmethod
    def set_input_panel_vars_from_dict(cls, context):
        """
        Set variables in Blender GUI to be the same as loaded file
        """

        config = cls.config_dict
        scene_config = config['scene']
        objects_config = config['objects']
        camera_config = config['camera']
        projector_config = config['projector']
        output_config = config['output']

        #Set scene variables
        context.scene.num_renders = scene_config['num_renders']
        context.scene.max_renders_per_scene = scene_config['max_renders_per_scene']
        context.scene.min_renders_per_scene = scene_config['min_renders_per_scene']
        
        #Import and move dropzone in blender
        if 'drop_zone' in bpy.data.objects.keys():

            bpy.data.objects['drop_zone'].location = scene_config['drop_zone_loc']
            bpy.data.objects['drop_zone'].scale = scene_config['drop_zone_scale']

        else:
            
            bpy.ops.mesh.primitive_cube_add()
            drop_zone = bpy.context.active_object
            mesh_name = drop_zone.name
            drop_zone.name = 'drop_zone'
            bpy.data.meshes[mesh_name].name = 'drop_zone_mesh'
            drop_zone.location = scene_config['drop_zone_loc']
            drop_zone.scale = scene_config['drop_zone_scale']
            
            bpy.ops.object.select_all(action='DESELECT')
            if drop_zone.select_get() is False:
                drop_zone.select_set(True)
            bpy.context.view_layer.objects.active = drop_zone
            bpy.ops.object.select_all(action='DESELECT')


        #Set camera variables
        context.scene.camera_focal_length = camera_config['focal_length']
        context.scene.camera_sensor_width = camera_config['sensor_width']
        camera_resolution = camera_config['resolution']
        context.scene.camera_resolution_height = camera_resolution[0]
        context.scene.camera_resolution_width = camera_resolution[1]
        context.scene.is_structured_light = camera_config['is_structured_light']

        #Set projector variables
        context.scene.projector_focal_length = projector_config['focal_length']
        context.scene.projector_sensor_width = projector_config['sensor_width']
        projector_resolution = projector_config['resolution']
        context.scene.camera_resolution_height = projector_resolution[0]
        context.scene.camera_resolution_width = projector_resolution[1]

        context.scene.projector_loc_vec = projector_config['proj2cam_pose']['location']
        rot = projector_config['proj2cam_pose']['rotation']
        if len(rot) == 3:
            context.scene.projector_rot_enum = 'xyz'
            context.scene.projector_rot_xyz = rot
        else:
            context.scene.projector_rot_enum = 'quat'
            context.scene.projector_rot_quat = rot



    @classmethod
    def write_to_pickle_file(cls, dir_path: str):
        dir_path = Path(bpy.path.abspath(dir_path)).resolve()
        filename = Path('DataPipe_input.pickle')
        
        path = Path.joinpath(dir_path, filename)

        if utility_fuctions.file_exists(path):

            exist = True
            index = 1
            
            while exist:
                
                filename = Path('DataPipe_input.{:04d}.pickle'.format(index))
                path = Path.joinpath(dir_path, filename)
                exist = utility_fuctions.file_exists(path)
                index += 1
        
        pickle_file = open(path, "wb")
        pickle.dump(cls.config_dict, pickle_file)
        pickle_file.close()

    @classmethod
    def input_from_file(cls, file_path: str):

        file_path = Path(bpy.path.abspath(file_path)).resolve()
        
        if file_path.suffix == '.pickle':
            pickle_file = open(file_path, "rb")
            cls.config_dict = pickle.load(pickle_file)
            print("-- Input loaded from file:\n{}".format(cls.config_dict))
        else:
            print("-- Filetype must be .pickle")