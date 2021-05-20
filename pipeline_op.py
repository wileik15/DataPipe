print("############ pipeline_op Start ############")
import bpy
from .src import config_module
from .src import utility_fuctions
from .src.camera_module import BlendCamera
from .src.scene_module import BlendScene
import numpy as np
import time

############## DO THIS FOR PIPELINE CLASSES ##############
#from .src import random_object

############ TEMPORARY ############
'''
import os
from pathlib import Path
resource_path = bpy.utils.resource_path(type='USER')
print("\nBlender resource path:\n{}".format(resource_path))
subfolder = "/util/test_img.jpg"
image_path = Path("{}/scripts/addons{}".format(resource_path,subfolder))
image_path.resolve()
print(str(image_path))
'''
###################################

############# SCENE OPERATORS #############
class DATAPIPE_OT_Set_up_Scene(bpy.types.Operator):

    bl_idname = 'datapipe.set_scene_parameters'
    bl_label = 'Set rendering engine to Cycles'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        utility_fuctions.initialize_pipeline_environment()

        return {'FINISHED'}

class DATAPIPE_OT_Append_camera_pose(bpy.types.Operator):

    bl_idname = 'datapipe.append_camera_pose'
    bl_label = 'Append pose'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        camera_pose_list = config_module.input_storage.config_dict['camera']['wrld2cam_pose_list']
        
        if context.scene.camera_rot_enum == 'quat':
            rot = context.scene.camera_rot_quat
            loc = context.scene.camera_loc_vec

        else:
            rot = context.scene.camera_rot_xyz
            loc = context.scene.camera_loc_vec

        transform, R, t = utility_fuctions.pose_to_tranformation_matrix(rotation=rot, location=loc)

        camera_pose_list.append(transform)

        ###### reseting camera pose props to zero
        context.scene.camera_loc_vec = (0,0,0)
        context.scene.camera_rot_quat = (1,0,0,0)
        context.scene.camera_rot_xyz = (0,0,0)

        print("\n### New pose added to camera pose list ###\n-> Utility camera pose list contains {} poses\n".format(len(config_module.input_storage.config_dict['camera']['wrld2cam_pose_list'])))

        return {'FINISHED'}

class DATAPIPE_OT_Remove_camera_pose(bpy.types.Operator):

    bl_idname = 'datapipe.remove_camera_pose'
    bl_label = 'Undo last'

    def execute(self, context):

        camera_pose_list = config_module.input_storage.config_dict['camera']['wrld2cam_pose_list']
        print("\nRemove camera pose RUNNING ...\nNumber of poses: {}\nType of pose list: {}\n".format(len(camera_pose_list), type(camera_pose_list)))

        if len(camera_pose_list) > 0:
            del camera_pose_list[-1]
            print("Number of poses in list after removal: {}".format(len(camera_pose_list)))

        return {'FINISHED'}


class DATAPIPE_OT_Preview_camera_pose(bpy.types.Operator):

    bl_idname = 'datapipe.preview_camera_pose'
    bl_label = 'Toggle camera preview'

    def execute(self, context):
        
        if 'temp_cam' in bpy.data.cameras.keys(): #Check if camera and projector temp object already exists
            #Remove camera object when toggeling off preview
            bpy.data.objects.remove(bpy.data.objects['temp_cam'], do_unlink=True) 
            bpy.data.cameras.remove(bpy.data.cameras['temp_cam'], do_unlink=True)

            if 'temp_projector' in bpy.data.lights.keys():
            #Remove projector object when toggeling off preview
                bpy.data.objects.remove(bpy.data.objects['temp_projector'], do_unlink=True)
                bpy.data.lights.remove(bpy.data.lights['temp_projector'], do_unlink=True)
        else:
            #Insert camera object in specified position for preview
            cam = bpy.data.cameras.new(name='temp_cam') #Create camera data
            cam_obj = bpy.data.objects.new(name='temp_cam', object_data=cam) #Create camera object
            bpy.context.scene.collection.objects.link(cam_obj)

            cam.sensor_width = context.scene.camera_sensor_width
            cam.lens = context.scene.camera_focal_length

            loc = context.scene.camera_loc_vec
            cam_obj.location = loc
            
            #Check rotation mode of camera
            if context.scene.camera_rot_enum == 'quat':
                cam_obj.rotation_mode = 'QUATERNION'
                rot = context.scene.camera_rot_quat
                cam_obj.rotation_quaternion = rot
            else:
                cam_obj.rotation_mode = 'XYZ'
                rot = context.scene.camera_rot_xyz
                cam_obj.rotation_euler = rot
            
            #Check if projector pose should be previewed
            if context.scene.is_structured_light:

                projector = bpy.data.lights.new(name='temp_projector', type='SPOT')
                projector_obj = bpy.data.objects.new(name='temp_projector', object_data=projector)
                bpy.context.scene.collection.objects.link(projector_obj)

                projector_obj.parent = cam_obj #Set projector to child of camera object
                projector_obj.parent_type = 'OBJECT'

                projector.spot_blend = 0
                projector.spot_size = 45*np.pi/180
                projector.shadow_soft_size = 0
                
                proj_loc = context.scene.projector_loc_vec
                projector_obj.location = proj_loc

                #Check rotation mode of projector
                if context.scene.projector_rot_enum == 'quat':
                    projector_obj.rotation_mode = 'QUATERNION'
                    proj_rot = context.scene.projector_rot_quat
                    projector_obj.rotation_quaternion = proj_rot
                else:
                    projector_obj.rotation_mode = 'XYZ'
                    proj_rot = context.scene.projector_rot_xyz
                    projector_obj.rotation_euler = proj_rot

        return {'FINISHED'}


class DATAPIPE_OT_Store_object_path(bpy.types.Operator):

    bl_idname = 'datapipe.store_object_path'
    bl_label = 'Append object to pipeline'

    def execute(self, context):

        object_filepath = context.scene.object_filepath

        #Append to a list or something

        ###################################
        # DO SOMETHING WITH THE PATH HERE #
        ###################################
        return {'FINISHED'}

class DATAPIPE_OT_Runner(bpy.types.Operator):

    bl_idname = 'datapipe.run_pipeline'
    bl_label = 'Run Pipeline'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        print('---- Now entering execute function')
        # Remove temp objects before running the pipeline, to avoid bugs.
        if 'temp_projector' in bpy.data.lights.keys(): #Remove projector object preview before running the pipeline
            bpy.data.objects.remove(bpy.data.objects['temp_projector'], do_unlink=True)
            bpy.data.lights.remove(bpy.data.lights['temp_projector'], do_unlink=True)
        
        if 'temp_cam' in bpy.data.cameras.keys(): #Remove camera object preview before running the pipeline
            bpy.data.objects.remove(bpy.data.objects['temp_cam'], do_unlink=True) 
            bpy.data.cameras.remove(bpy.data.cameras['temp_cam'], do_unlink=True)
        
        if 'temp_object' in bpy.data.objects.keys(): #Remove object preview before running the pipeline
            bpy.data.objects.remove(bpy.data.objects['temp_object'], do_unlink=True)
            bpy.data.materials.remove(bpy.data.materials['temp_material'], do_unlink=True)

        # Load all information from GUI to config dict
        config = config_module.input_storage.config_dict

        camera_config = config['camera']
        projector_config = config['projector']
        scene_config = config['scene']
        objects_config = config['objects']

        #Scene inputs
        scene_config['num_renders'] = context.scene.num_renders
        scene_config['max_renders_per_scene'] = context.scene.max_renders_per_scene
        scene_config['min_renders_per_scene'] = context.scene.min_renders_per_scene

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
        loc = context.scene.projector_loc_vec
        if context.scene.projector_rot_enum == 'quat':
            rot = context.scene.projector_rot_quat
        else:
            rot = context.scene.projector_rot_xyz
        transform, R, t = utility_fuctions.pose_to_tranformation_matrix(rotation=rot, location=loc)
        projector_config['proj2cam_pose'] = transform


        ################### PIPELINE FROM HERE ON OUT ###################
        print("\nPIPELINE RUN INITIATED\n")
        start_time = time.time()

        camera = BlendCamera(camera_name='pipe_cam',config=config)

        loop_finished = False
        
        while not loop_finished:

            scene = BlendScene(config=config, camera=camera)
            
            for render in range(scene.renders_for_scene):

                print("### Scene {} Render {}".format(scene.scene_num, render))
            loop_finished = scene.last_scene


        end_time = time.time()

        print("##################\n# Timing results #\n# Run time: {:2.2f} #\n##################\n".format(end_time-start_time))
        print("\nPIPELINE RUN FINISHED\n")
        return {'FINISHED'}


classes = [
           DATAPIPE_OT_Store_object_path,
           DATAPIPE_OT_Append_camera_pose,
           DATAPIPE_OT_Preview_camera_pose,
           DATAPIPE_OT_Runner,
           DATAPIPE_OT_Remove_camera_pose,
           DATAPIPE_OT_Set_up_Scene,
          ]
    
def register():
    for cl in classes:
        try:
            bpy.utils.register_class(cl)
        except RuntimeError as e:
            print(e)

def unregister():
    for cl in classes:
        try:
            bpy.utils.unregister_class(cl)
        except RuntimeError:
            pass

print("############ pipeline_op End ############")