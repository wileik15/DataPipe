print("############ pipeline_op Start ############")
import bpy
from .src import config_module
from .src import utility_fuctions

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
            rot = context.sce.camera_rot_quat
            loc = context.scene.camera_loc_vec

        else:
            rot = context.scene.camera_rot_xyz
            loc = context.scene.camera_loc_vec

        transform, R, t = utility_fuctions.pose_to_tranformation_matrix(rotation=rot, location=loc)

        camera_pose_list.append(transform)

        print("\n#############################\nUtility camera pose list after appending camera pose:\n{}\n#############################\n".format(config_module.input_storage.config_dict['camera']['wrld2cam_pose_list']))

        return {'FINISHED'}

class DATAPIPE_OT_Preview_camera_pose(bpy.types.Operator):

    bl_idname = 'datapipe.preview_camera_pose'
    bl_label = 'Toggle camera pos preview:'

    def execute(self, context):
        camera_names = bpy.data.cameras.keys()
        if 'temp_cam' in camera_names:
            bpy.data.objects.remove(bpy.data.objects['temp_cam'], do_unlink=True)
            bpy.data.cameras.remove(bpy.data.cameras['temp_cam'], do_unlink=True)
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
        
        ############################
        # Pipeline loop going here #
        ############################

        print("######################\nThe chosen path is\n{}\n######################".format(context.scene.output_path))

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

'''
class DATAPIPE_OT_Filebrowser(bpy.types.Operator):
    bl_idname = "datapipe.open_filebrowser"
    bl_label = "Set filepath"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filepaths = []
    #somewhere to remember the address of the file


    def execute(self, context):
        #############
        # TEMPORARY #
        #############
        display = "filepath= " + self.filepath  
        print(display) #Prints to console

        if self.filepath[-3:] == 'obj':
            bpy.ops.import_scene.obj(filepath=self.filepath)
            obj = bpy.context.active_object
            print("Active object: {}".format(obj.name))
            obj.name = "temp_obj"
        else:
            print("Only .obj files are supported.")

        return {'FINISHED'}

    def invoke(self, context, event): # See comments at end  [1]

        context.window_manager.fileselect_add(self)
        #Open browser, take reference to 'self' 
        #read the path to selected file, 
        #put path in declared string type data structure self.filepath

        self.filepaths.append(self.filepath)

        return {'RUNNING_MODAL'}  
        # Tells Blender to hang on for the slow user input


#Tell Blender this exists and should be used


# [1] In this invoke(self, context, event) is being triggered by the below command
#but in your script you create a button or menu item. When it is clicked
# Blender runs   invoke()  automatically.

#execute(self,context) prints self.filepath as proof it works.. I hope.


#bpy.ops.open.browser('INVOKE_DEFAULT')
'''