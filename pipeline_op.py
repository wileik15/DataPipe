print("############ pipeline_op Start ############")
from pathlib import Path
import bpy
from .src import utility_fuctions
from .src import config_module
from .src.camera_module import BlendCamera
from .src.scene_module import BlendScene
from .src.objects_module import ObjectManager
from .src.render_module import Renderer
from .src.simulation_module import Simulation
from .src.structured_light_module import Algorithm
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
            mesh_name = drop_zone.name
            drop_zone.name = 'drop_zone'
            bpy.data.meshes[mesh_name].name = 'drop_zone_mesh'
            drop_zone.location = (0, 0, 2)
            drop_zone.scale = (0.5, 0.5, 0.5)

            bpy.ops.object.select_all(action='DESELECT')
            
            if drop_zone.select_get() is False:
                drop_zone.select_set(True)

            print("Objects in view layer:\n{}".format(bpy.context.view_layer.objects))
            bpy.context.view_layer.objects.active = drop_zone
            bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}

############# OBJECT OPERATORS #############
class DATAPIPE_OT_Preview_object(bpy.types.Operator):

    bl_idname = 'datapipe.preview_object'
    bl_label = 'Toggle object preview'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        filepath = Path(bpy.path.abspath(context.scene.object_path)).resolve() #Filepath from input
        print("Filepath of object:\n{}\nwith type: {}".format(filepath, type(filepath))) 

        scale = context.scene.object_scale
        ob_scale = [scale, scale, scale] #object scale from input
        print("Scaling type is {}".format(type(ob_scale)))

        
        if filepath.suffix == '.obj': #Filetype has to be .obj

            if 'temp_collection' not in bpy.data.collections.keys(): #Check for earlier import

                temp_collection = bpy.data.collections.new(name='temp_collection')
                bpy.context.scene.collection.children.link(temp_collection) #Link to scene collection

            temp_collection = bpy.data.collections['temp_collection']

            if 'temp_object' not in bpy.data.objects.keys() and 'temp_material' not in bpy.data.materials.keys():
                bpy.ops.import_scene.obj(filepath=str(filepath))
                print("\nImported .obj file contains {} objects:\n{}\n".format(len(list(bpy.context.selected_objects)), list(bpy.context.selected_objects)))
                if len(bpy.context.selected_objects) != 1: #Only one object can be imported at a time
                    for ob in bpy.context.selected_objects:
                        #Remove belonging data
                        bpy.data.materials.remove(ob.active_material, do_unlink=True)
                        bpy.data.objects.remove(ob, do_unlink=True)
                        bpy.data.meshes.remove(bpy.data.meshes[ob.name], do_unlink=True)
                    print("Input .obj file can only contain one object")
                else:
                    ob = bpy.context.selected_objects[0] #Get object
                    
                    ob.users_collection[0].objects.unlink(ob) #Remove object from default collection
                    temp_collection.objects.link(ob) #Link to temp collection

                    mesh_name = ob.name #Store current mesh name

                    ob.name = 'temp_object'
                    ob.scale = ob_scale #Set scale from input

                    ob_mat = ob.active_material #ob material data
                    ob_mat.name = 'temp_material'

                    bpy.data.meshes[mesh_name].name = 'temp_mesh' #ob mesh data

                    print("     Object {}\n     material:\n     {}".format(ob.name, ob.active_material))
            else:
                if 'temp_object' in bpy.data.objects:
                    bpy.data.objects.remove(bpy.data.objects['temp_object'], do_unlink=True)
                    bpy.data.meshes.remove(bpy.data.meshes['temp_mesh'], do_unlink=True)
                    if 'temp_material' in bpy.data.materials:
                        bpy.data.materials.remove(bpy.data.materials['temp_material'], do_unlink=True)
                else:
                    bpy.data.materials.remove(bpy.data.materials['temp_material'], do_unlink=True)
        else:
            print("Required filetype for object is \".obj\".")

        return {'FINISHED'}

class DATAPIPE_OT_Append_object_data(bpy.types.Operator):

    bl_idname = 'datapipe.append_object_data'
    bl_label = 'Append object to pipeline'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object_config = config_module.input_storage.config_dict['objects'] #Get object config
        objects_list = object_config['objects_list']

        #User inputs
        object_filepath = Path(bpy.path.abspath(context.scene.object_path)).resolve()
        object_scale = context.scene.object_scale
        object_mass = context.scene.object_mass
        object_collision_shape = context.scene.object_collision_shape
        object_instances_max = context.scene.object_instances_max
        object_instances_min = context.scene.object_instances_min

        objects_list.append({'filepath': object_filepath, 'scale': object_scale, 'mass': object_mass, 'collision_shape': object_collision_shape, 'max': object_instances_max, 'min': object_instances_min}) #Append user input to config dict

        if 'temp_object' in bpy.data.objects.keys(): #Remove object data
            bpy.data.objects.remove(bpy.data.objects['temp_object'], do_unlink=True)
            bpy.data.materials.remove(bpy.data.materials['temp_material'], do_unlink=True)
            bpy.data.meshes.remove(bpy.data.meshes['temp_mesh'], do_unlink=True)

        print("Object config after appending:\n{}\n".format(config_module.input_storage.config_dict['objects']))

        print("__file__: {}".format(__file__))
        return {'FINISHED'}


class DATAPIPE_OT_Remove_last_object_data(bpy.types.Operator):

    bl_idname = 'datapipe.remove_last_object_data'
    bl_label = 'Remove last'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object_config = config_module.input_storage.config_dict['objects']
        object_list = object_config['objects_list']

        if len(object_list) > 0: #Check if any objects in list
            del object_list[-1] #Remove last object

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
    bl_options = {'REGISTER', 'UNDO'}

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
            bpy.data.materials.remove(bpy.data.materials['temp_material'], do_unlink=True)
            bpy.data.objects.remove(bpy.data.objects['temp_object'], do_unlink=True)
            bpy.data.meshes.remove(bpy.data.meshes['temp_mesh'], do_unlink=True)
        
        if 'temp_collection' in bpy.data.collections.keys(): #Remove collections preview before running the pipeline
            bpy.data.collections.remove(bpy.data.collections['temp_collection'], do_unlink=True)

        # Load all information from GUI to config dict
        config_module.input_storage.write_to_config_dict(context)

        ################### PIPELINE FROM HERE ON OUT ###################
        print("\n###################\nPIPELINE RUN INITIATED\n###################\n")
        start_time = time.time()

        config = config_module.input_storage.config_dict

        camera = BlendCamera(camera_name='pipe_cam',config=config)

        renderer = Renderer(camera=camera)

        object_manager = ObjectManager(config=config)

        loop_finished = False

        while not loop_finished:
            
            #Prep simulation goes here.

            scene = BlendScene(config=config, camera=camera, object_manager=object_manager)

            object_manager.import_objects()

            object_manager.create_initial_positions(scene=scene)

            #Simulation goes here
            simulation = Simulation(sim_end=400)
            simulation.run_loop() #Loop physics simulation
            simulation.apply_simulated_transforms(object_manager=object_manager)

            #Object transformation applied after simulation
            print("++++++ Checkpoint {}".format(scene.scene_name))
            
            for render in range(1,scene.renders_for_scene+1):
                
                renderer.set_output_paths(scene=scene, render_num=render)

                camera.move(curr_render=render)

                scene.write_output_info_to_scene_dict(render_num=render, camera=camera, object_manager=object_manager)

                #Render scene goes here
                print("\nRENDERING {} CAMERA ANGLE {}/{}".format(scene.scene_name, render, scene.renders_for_scene))
                renderer.render_results()

                if camera.is_structured_light:
                    SL_algorithm = Algorithm(renderer=renderer, pattern_names=camera.pattern_names)

                print("++++++ Checkpoint Render {}".format(render))
            
            scene.write_scene_dict_to_file()

            loop_finished = scene.last_scene
            print("++++++ Checkpoint {}".format('Loop finished'))

            del scene

        BlendScene.reset_scene_number()
        config_module.input_storage.reset_config_dict()

        print("After reseting scene class, scene number is: {}".format(BlendScene.scene_num))
        end_time = time.time()

        print("##################\n# Timing results #\n# Run time: {:2.2f} #\n##################\n".format(end_time-start_time))
        print("\nPIPELINE RUN FINISHED\n")
        return {'FINISHED'}


classes = [
           DATAPIPE_OT_Set_up_Scene,
           DATAPIPE_OT_Load_input_file,
           DATAPIPE_OT_Import_dropzone_object,
           DATAPIPE_OT_Preview_object,
           DATAPIPE_OT_Append_object_data,
           DATAPIPE_OT_Remove_last_object_data,
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