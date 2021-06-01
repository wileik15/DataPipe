from os import name
import bpy
import numpy as np
from .src.config_module import input_storage

print("############ pipeline_panel Start ############")

class DATAPIPE_PT_Start_panel(bpy.types.Panel):
    bl_idname = 'Start_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DataPipe'
    bl_label = "Initialize pipeline"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 2
        row.operator('datapipe.set_scene_parameters', icon='PLAY')

        box = layout.box()
        box.label(text='Load pipeline input from pickle file')

        row = box.row()
        col = row.column()
        col.prop(context.scene, 'load_pipeline_input_path')
        col = row.column()
        col.scale_x = 0.7
        col.operator('datapipe.load_input_file', icon='IMPORT')


class DATAPIPE_PT_scenes_panel(bpy.types.Panel):
    bl_idname = 'Scenes_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DataPipe'
    bl_label = "Scene inputs"

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        row = box.split(factor=0.6)
        left_col = row.column()
        right_col = row.column()

        #Total number of renders input
        row = left_col.row()
        row.alignment = 'RIGHT'
        row.label(text='Total number of renders')
        row = right_col.row()
        row.prop(context.scene, 'num_renders')

        #Max renders input
        row = left_col.row()
        row.alignment = 'RIGHT'
        row.label(text='Renders per scene Max')
        row = right_col.row()
        row.prop(context.scene, 'max_renders_per_scene')

        #Min renders input
        row = left_col.row()
        row.alignment = 'RIGHT'
        row.label(text='Min')
        row = right_col.row()
        row.prop(context.scene, 'min_renders_per_scene')

        row = layout.row()

        #Dropzone inputs
        box = layout.box()
        row = box.row()
        row.operator('datapipe.import_dropzone_object', icon='PIVOT_BOUNDBOX')
        row = box.row()
        row.label(text='Move the box to desired location')

        


class DATAPIPE_PT_objects_panel(bpy.types.Panel):
    bl_idname = 'Objects_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DataPipe'
    bl_label = "Objects inputs"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.label(text="Object filepath:", icon='OUTLINER_OB_MESH')
        row = layout.row()
        row.prop(context.scene, 'object_path')

        box = layout.box()

        row = box.split(factor=0.5)

        left_col = row.column()
        right_col = row.column()

        row = left_col.row()
        row.alignment = 'RIGHT'
        row.label(text='Scaling factor')

        row = left_col.row()
        row.alignment = 'RIGHT'
        row.label(text='Instances in scene Max')

        row = left_col.row()
        row.alignment = 'RIGHT'
        row.label(text='Min')

        row = right_col.row()
        row.prop(context.scene, 'object_scale')

        row = right_col.row()
        row.prop(context.scene, 'object_instances_max')

        row = right_col.row()
        row.prop(context.scene, 'object_instances_min')

        box = layout.box()
        row = box.row()
        row.operator('datapipe.preview_object', icon='WORKSPACE')

        row = box.row()

        row = box.row()
        left_col = row.column()
        right_col = row.column()

        row = left_col.row()
        row.scale_y = 2
        row.operator('datapipe.append_object_data', icon='FILE_NEW')

        row = right_col.row()
        row.scale_y = 2
        row.operator('datapipe.remove_last_object_data', icon='TRASH')




class DATAPIPE_PT_camera_panel(bpy.types.Panel):
    bl_idname = 'Camera_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DataPipe'
    bl_label = "Camera inputs"
    

    def draw(self, context):

        layout = self.layout

        #Camera intrinsics
        row = layout.row()
        row.label(text='Camera intrinsics', icon='CAMERA_DATA')
        row = layout.split(factor=0.5)
        
        left_col = row.column()
        right_col = row.column()

        #Focal length input
        row = left_col.row()
        row.alignment = 'RIGHT'
        row.label(text='Focal length')
        row = right_col.row()
        row.prop(context.scene, 'camera_focal_length')

        #Sensor width input
        row = left_col.row()
        row.alignment = 'RIGHT'
        row.label(text='Sensor width')
        row = right_col.row()
        row.prop(context.scene, 'camera_sensor_width')

        row = left_col.row()
        row.alignment = 'RIGHT'
        row.label(text='Resolution height')
        row = left_col.row()
        row.alignment = 'RIGHT'
        row.label(text='width')

        row = right_col.row()
        row.prop(context.scene, 'camera_resolution_height')

        row = right_col.row()
        row.prop(context.scene, 'camera_resolution_width')
        
        #Structured light
        row = layout.row()
        row.prop(context.scene, 'is_structured_light')

        if context.scene.is_structured_light:

            #Projector intrinsics

            box = layout.box()
            row = box.row()
            row.label(text='Projector intrinsics', icon='LIGHT')
            row = box.split(factor=0.5)

            left_col = row.column()
            right_col = row.column()

            row = left_col.row()
            row.alignment = 'RIGHT'
            row.label(text='Focal length')
            row = right_col.row()
            row.prop(context.scene, 'projector_focal_length')

            row = left_col.row()
            row.alignment = 'RIGHT'
            row.label(text='Sensor width')
            row = right_col.row()
            row.prop(context.scene, 'projector_sensor_width')
            
            row = left_col.row()
            row.alignment = 'RIGHT'
            row.label(text='Resolution height')
            right_col.column(align=True)
            row = right_col.row()
            row.prop(context.scene, 'projector_resolution_height')
            
            row = left_col.row()
            row.alignment = 'RIGHT'
            row.label(text='width')
            row = right_col.row()
            row.prop(context.scene, 'projector_resolution_width')


            #Projector extrinsics
            box = layout.box()
            row = box.row()
            row.label(text="Location (x, y, z) relative to camera", icon='EMPTY_AXIS')

            row = box.row()
            row.prop(context.scene, 'projector_loc_vec')

            row = box.row()
            row.label(text='Rotation relative to camera', icon='SPHERE')

            row = box.row()
            row.prop(context.scene, 'projector_rot_enum')

            row = box.row()
            if context.scene.projector_rot_enum == 'xyz':
                row.prop(context.scene, 'projector_rot_xyz')
            else:
                row.prop(context.scene, 'projector_rot_quat')

        row = layout.row()
        row.label(text='')

        row = layout.row()
        row.operator('datapipe.preview_camera_pose', icon='WORKSPACE')

        row = layout.row()
        row.label(text='Move camera to desired pose')
        row = layout.row()
        row.scale_y = 2.0
        row.operator('datapipe.append_camera_pose', icon='FILE_NEW')

        col = row.column()
        col.operator('datapipe.remove_camera_pose', icon='TRASH')




class DATAPIPE_PT_run_panel(bpy.types.Panel):
    bl_idname = 'Run_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DataPipe'
    bl_label = "Run pipeline"

    def draw(self, context):

        layout = self.layout
        box = layout.box()

        row = box.row()
        row.label(text="Save pipeline input to file")

        row = box.row()
        col = row.column()
        col.prop(context.scene, 'save_pipeline_input_path')

        col = row.column()
        col.scale_x = 0.7
        col.operator('datapipe.save_pipeline_info', icon='EXPORT')
        
        row = layout.row()

        box = layout.box()
        row = box.row()
        row.label(text='Save pipeline output to:')
        row = box.row()
        row.prop(context.scene, 'pipeline_output_path')

        row = box.row()
        row = box.row()
        row.operator('datapipe.run_pipeline', icon='PLAY')

        

classes = [
           DATAPIPE_PT_Start_panel,
           DATAPIPE_PT_scenes_panel,
           DATAPIPE_PT_objects_panel,
           DATAPIPE_PT_camera_panel,
           DATAPIPE_PT_run_panel
          ]

def register():
    ##############################################
    ####### INITIALIZE PIPELINE PROPERTIES #######
    ##############################################
    bpy.types.Scene.load_pipeline_input_path = bpy.props.StringProperty(
        name='',
        subtype='FILE_PATH',
        description='Filepath to pickle file containing pipeline inputs')

    ################################
    ####### SCENE PROPERTIES #######
    ################################
    bpy.types.Scene.num_renders = bpy.props.IntProperty(
        name='', 
        default=1,
        description='Number of images to render')
    bpy.types.Scene.max_renders_per_scene = bpy.props.IntProperty(
        name='',
        default=1,
        description='The max number of camera poses rendered per scene configuration')
    bpy.types.Scene.min_renders_per_scene = bpy.props.IntProperty(
        name='',
        default=1,
        description='The min number of camera poses rendered per scene configuration')
    
    #################################
    ####### OBJECT PROPERTIES #######
    #################################
    bpy.types.Scene.object_path = bpy.props.StringProperty(
        name='',
    subtype='FILE_PATH',
    description='Filepath to object included in pipeline')
    bpy.types.Scene.object_scale = bpy.props.FloatProperty(
        name='',
        soft_min=0,
        description='Scaling of the object. Used to ensure that the 3D model\'s units are equal to scene units',
        default=1)
    bpy.types.Scene.object_instances_max = bpy.props.IntProperty(
        name='',
        soft_min=0,
        default=2,
        description='Maximum number of object instance in each scene.')
    bpy.types.Scene.object_instances_min = bpy.props.IntProperty(
        name='',
        soft_min=0,
        default=0,
        description='Minimum number of object instance in each scene.')

    #################################
    ####### CAMERA PROPERTIES #######
    #################################
    bpy.types.Scene.camera_focal_length = bpy.props.FloatProperty(
        name='',
        unit='CAMERA')
    bpy.types.Scene.camera_sensor_width = bpy.props.FloatProperty(
        name='',
        unit='CAMERA')
    bpy.types.Scene.camera_resolution_height = bpy.props.IntProperty(
        name='',
        default= 480,
        subtype='PIXEL')
    bpy.types.Scene.camera_resolution_width = bpy.props.IntProperty(
        name='',
        default= 720,
        subtype='PIXEL')
    bpy.types.Scene.is_structured_light = bpy.props.BoolProperty(
        name='Structured light',
        description='Toggles on structured light rendering. The pipeline process will be slower, but the results will be realistic noise on rendered dataset')
    
    ####################################
    ####### PROJECTOR PROPERTIES #######
    ####################################
    bpy.types.Scene.projector_focal_length = bpy.props.FloatProperty(
        name='',
        unit='CAMERA')
    bpy.types.Scene.projector_sensor_width = bpy.props.FloatProperty(
        name='',
        unit='CAMERA')
    bpy.types.Scene.projector_resolution_height = bpy.props.IntProperty(
        name='',
        default= 480,
        subtype='PIXEL')
    bpy.types.Scene.projector_resolution_width = bpy.props.IntProperty(
        name='',
        default= 720,
        subtype='PIXEL')
    bpy.types.Scene.projector_loc_vec = bpy.props.FloatVectorProperty(
        name='',
        default=(-0.15, 0, 0),
        unit='LENGTH')
    bpy.types.Scene.projector_rot_enum = bpy.props.EnumProperty(
        name='',
        items=[('xyz', 'XYZ Euler angles', ''),
               ('quat', 'Quaternions [w, x, y, z]', '')])
    bpy.types.Scene.projector_rot_xyz = bpy.props.FloatVectorProperty(
        name='',
        default= (0, -np.pi/180*8.5, 0),
        unit='ROTATION')
    bpy.types.Scene.projector_rot_quat = bpy.props.FloatVectorProperty(
        name='',
        default= (0.9972502, 0, -0.0741085, 0),
        size=4)
    
    ######################################
    ####### OUTPUT PATH PROPERTIES #######
    ######################################
    bpy.types.Scene.output_path = bpy.props.StringProperty(
        name='',
        subtype='DIR_PATH')

    #######################################
    ####### RUN PIPELINE PROPERTIES #######
    #######################################
    bpy.types.Scene.save_pipeline_input_path = bpy.props.StringProperty(
        name='',
        subtype='DIR_PATH')
    bpy.types.Scene.pipeline_output_path = bpy.props.StringProperty(
        name='',
        subtype='DIR_PATH',
        description='Directory to save output from pipeline run.')

    for cl in classes:
        bpy.utils.register_class(cl)

def unregister():
    ##############################################
    ####### INITIALIZE PIPELINE PROPERTIES #######
    ##############################################
    del bpy.types.Scene.load_pipeline_input_path

    ################################
    ####### SCENE PROPERTIES #######
    ################################
    del bpy.types.Scene.num_renders
    del bpy.types.Scene.max_renders_per_scene
    del bpy.types.Scene.min_renders_per_scene

    #################################
    ####### OBJECT PROPERTIES #######
    #################################
    del bpy.types.Scene.object_path
    del bpy.types.Scene.object_scale
    del bpy.types.Scene.object_instances_max
    del bpy.types.Scene.object_instances_min

    #################################
    ####### CAMERA PROPERTIES #######
    #################################
    del bpy.types.Scene.camera_focal_length
    del bpy.types.Scene.camera_sensor_width
    del bpy.types.Scene.camera_resolution_height
    del bpy.types.Scene.camera_resolution_width
    del bpy.types.Scene.is_structured_light

    ####################################
    ####### PROJECTOR PROPERTIES #######
    ####################################
    del bpy.types.Scene.projector_focal_length
    del bpy.types.Scene.projector_sensor_width
    del bpy.types.Scene.projector_resolution_height
    del bpy.types.Scene.projector_resolution_width
    del bpy.types.Scene.projector_loc_vec
    del bpy.types.Scene.projector_rot_enum
    del bpy.types.Scene.projector_rot_xyz
    del bpy.types.Scene.projector_rot_quat

    ######################################
    ####### OUTPUT PATH PROPERTIES #######
    ######################################
    del bpy.types.Scene.output_path

    #######################################
    ####### RUN PIPELINE PROPERTIES #######
    #######################################
    del bpy.types.Scene.save_pipeline_input_path
    del bpy.types.Scene.pipeline_output_path

    for cl in classes:
        bpy.utils.unregister_class(cl)

print("############ pipeline_panel End ############")