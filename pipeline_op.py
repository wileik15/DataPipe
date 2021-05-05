print("############ pipeline_op Start ############")
import bpy
from .src import config_module
from .src import utility_fuctions
import numpy as np

############## DO THIS FOR PIPELINE CLASSES ##############
#from .src import random_object

############ TEMPORARY ############

import os
from pathlib import Path
resource_path = bpy.utils.resource_path(type='USER')
print("\nBlender resource path:\n{}".format(resource_path))
subfolder = "/util/test_img.jpg"
image_path = Path("{}/scripts/addons{}".format(resource_path,subfolder))
image_path.resolve()
print(str(image_path))

###################################

class DATAPIPE_OT_Append_camera_pose(bpy.types.Operator):

    bl_idname = 'datapipe.append_camera_pose'
    bl_label = 'Append camera pose'
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

        print("\n#############################\nUtility camera pose list after appending camera pose:\n{}\n#############################\n".format(config_module.input_storage.config_dict['camera']['wrld2cam_pose_list']))

        return {'FINISHED'}

class DATAPIPE_OT_Preview_camera_pose(bpy.types.Operator):

    bl_idname = 'datapipe.preview_camera_pose'
    bl_label = 'Toggle camera pose preview'

    def execute(self, context):
        camera_names = bpy.data.cameras.keys()
        if 'temp_cam' in camera_names:
            bpy.data.objects.remove(bpy.data.objects['temp_cam'], do_unlink=True)
            bpy.data.cameras.remove(bpy.data.cameras['temp_cam'], do_unlink=True)
            if 'temp_projector' in bpy.data.lights.keys():
                bpy.data.objects.remove(bpy.data.objects['temp_projector'], do_unlink=True)
                bpy.data.lights.remove(bpy.data.lights['temp_projector'], do_unlink=True)
        else:
            cam = bpy.data.cameras.new(name='temp_cam') #Create camera data
            cam_obj = bpy.data.objects.new(name='temp_cam', object_data=cam) #Create camera object
            bpy.context.scene.collection.objects.link(cam_obj)

            cam.sensor_width = context.scene.camera_sensor_width
            cam.lens = context.scene.camera_focal_length

            loc = context.scene.camera_loc_vec
            cam_obj.location = loc

            if context.scene.camera_rot_enum == 'quat':
                rot = context.scene.camera_rot_quat
                cam_obj.rotation_quaternion = rot
                
            else:
                rot = context.scene.camera_rot_xyz
                cam_obj.rotation_euler = rot
            
            if context.scene.is_structured_light:

                projector = bpy.data.lights.new(name='temp_projector', type='SPOT')
                projector_obj = bpy.data.objects.new(name='temp_projector', object_data=projector)
                bpy.context.scene.collection.objects.link(projector_obj)

                projector_obj.parent = cam_obj
                projector_obj.parent_type = 'OBJECT'

                projector.spot_blend = 0
                projector.spot_size = np.pi
                projector.shadow_soft_size = 0
                
                proj_loc = context.scene.projector_loc_vec
                projector_obj.location = proj_loc
                if context.scene.projector_rot_enum == 'quat':
                    proj_rot = context.scene.projector_rot_quat
                    projector_obj.rotation_quaternion = proj_rot
                else:
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
        
        config = config_module.input_storage.config_dict
        camera_config = config['camera']
        projector_config = config['projector']
        scene_config = config['scene']
        objects_config = config['objects']

        camera_config['focal_length'] = context.scene.camera_focal_length
        camera_config['sensor_width'] = context.scene.camera_sensor_width
        camera_config['resolution'] = [context.scene.camera_resolution_height, context.scene.camera_resolution_width]
        camera_config['is_structured_light'] = context.scene.is_structured_light

        return {'FINISHED'}


classes = [
           DATAPIPE_OT_Append_camera_pose,
           DATAPIPE_OT_Runner,
           DATAPIPE_OT_Store_object_path,
           DATAPIPE_OT_Preview_camera_pose
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