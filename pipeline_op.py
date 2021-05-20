print("############ pipeline_op Start ############")
import bpy
from bpy.types import Mesh, Scene
from .src import config_module
from .src import utility_fuctions
from .src.camera_module import BlendCamera
from .src.scene_module import BlendScene
import numpy as np
import time

############## DO THIS FOR PIPELINE CLASSES ##############
#from .src import random_object


############# SCENE OPERATORS #############
class DATAPIPE_OT_Set_up_Scene(bpy.types.Operator):

    bl_idname = 'datapipe.set_scene_parameters'
    bl_label = 'Initialize pipeline'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        utility_fuctions.initialize_pipeline_environment()

        return {'FINISHED'}

class DATAPIPE_OT_Load_input_file(bpy.types.Operator):

    bl_idname = 'datapipe.load_input_file'
    bl_label = 'Load'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        #Load all input from file to configmodule.input_storage
        config_module.input_storage.input_from_file(context.scene.load_pipeline_input_path)
        
        config_module.input_storage.set_input_panel_vars_from_dict(context)

        return {'FINISHED'}

class DATAPIPE_OT_Import_dropzone_object(bpy.types.Operator):

    bl_idname = 'datapipe.import_dropzone_object'
    bl_label = 'Import dropzone'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        if 'drop_zone' not in bpy.data.objects:
            bpy.ops.mesh.primitive_cube_add()
            drop_zone = bpy.context.active_object
            drop_zone.name = 'drop_zone'
            drop_zone.location = (0, 0, 2)
            drop_zone.scale = (0.5, 0.5, 0.5)

            bpy.ops.object.select_all(action='DESELECT')
            
            if drop_zone.select_get() is False:
                drop_zone.select_set(True)

            print("Objects in view layer:\n{}".format(bpy.context.view_layer.objects))
            bpy.context.view_layer.objects.active = drop_zone
            #bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
            bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}

############# CAMERA OPERATORS #############
class DATAPIPE_OT_Append_camera_pose(bpy.types.Operator):

    bl_idname = 'datapipe.append_camera_pose'
    bl_label = 'Append pose'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        camera_pose_list = config_module.input_storage.config_dict['camera']['wrld2cam_pose_list']
        
        if 'temp_cam' in bpy.data.cameras.keys():
            cam = bpy.data.objects['temp_cam']
            
            loc = list(cam.location)
            cam.rotation_mode = 'QUATERNION'
            rot = list(cam.rotation_quaternion)
            print("Appended pose is:\n--> Loc: {}\n--> Rot: {}".format(loc, rot))
            transform = {'rotation': rot, 'location': loc}

            camera_pose_list.append(transform)

            ###### reseting camera pose props to zero
            cam.location = (0, 0, 1)
            cam.rotation_mode = 'XYZ'
            cam.rotation_euler = (np.pi/2, 0, 0)

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
            
            #Set default pose
            cam_obj.location = (0,0,1)
            cam_obj.rotation_euler = (np.pi/2, 0, 0)
            
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

class DATAPIPE_OT_Save_pipeline_info(bpy.types.Operator):

    bl_idname = 'datapipe.save_pipeline_info'
    bl_label = 'Export'

    def execute(self, context):

        config_module.input_storage.write_to_config_dict(context)

        print("\nconfig dict after loading info:\n{}".format(config_module.input_storage.config_dict))

        config_module.input_storage.write_to_pickle_file(context.scene.save_pipeline_input_path)

        return {'FINISHED'}


############# RUN PIPELINE OPERATORS #############
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
        config_module.input_storage.write_to_config_dict(context)

        ################### PIPELINE FROM HERE ON OUT ###################
        print("\nPIPELINE RUN INITIATED\n")
        start_time = time.time()

        config = config_module.input_storage.config_dict

        camera = BlendCamera(camera_name='pipe_cam',config=config)

        loop_finished = False
        i = 0
        while not loop_finished and i < 20:

            scene = BlendScene(config=config, camera=camera)
            i+=1
            
            for render in range(scene.renders_for_scene):

                print("Rendering... Scene {} Render {}".format(scene.scene_number, render+1))
            loop_finished = scene.last_scene
            del scene


        end_time = time.time()

        print("##################\n# Timing results #\n# Run time: {:2.2f} #\n##################\n".format(end_time-start_time))
        print("\nPIPELINE RUN FINISHED\n")
        return {'FINISHED'}


classes = [
           DATAPIPE_OT_Set_up_Scene,
           DATAPIPE_OT_Load_input_file,
           DATAPIPE_OT_Import_dropzone_object,
           DATAPIPE_OT_Store_object_path,
           DATAPIPE_OT_Preview_camera_pose,
           DATAPIPE_OT_Append_camera_pose,
           DATAPIPE_OT_Remove_camera_pose,
           DATAPIPE_OT_Save_pipeline_info,
           DATAPIPE_OT_Runner,
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