import bpy
import numpy as np

print("############ pipeline_panel Start ############")

class DATAPIPE_PT_scenes_panel(bpy.types.Panel):
    bl_idname = 'Scenes_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DataPipe'
    bl_label = "Scene inputs"

    def draw(self, context):

        layout = self.layout

        layout.label(text="Scene Inputs")

        


class DATAPIPE_PT_objects_panel(bpy.types.Panel):
    bl_idname = 'Objects_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DataPipe'
    bl_label = "Objects inputs"

    def draw(self, context):

        layout = self.layout

        layout.label(text="Objects Inputs")



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
        row.label(text='Intrinsic parameters', icon='CAMERA_DATA')

        row = layout.row()
        row.prop(context.scene, 'camera_focal_length')

        row = layout.row()
        row.prop(context.scene, 'camera_sensor_width')
        
        col = layout.column(align=True)
        
        row = col.row()
        row.prop(context.scene, 'camera_resolution_height')

        row = col.row()
        row.prop(context.scene, 'camera_resolution_width')


        #Camera extrinsics
        row = layout.row()
        row.label(text="Location (X, Y, Z)", icon='EMPTY_AXIS')

        row = layout.row()
        row.prop(context.scene, 'camera_loc_vec')

        row = layout.row()
        row.label(text='Rotation', icon='SPHERE')

        row = layout.row()
        row.prop(context.scene, 'camera_rot_enum')

        row = layout.row()
        if context.scene.camera_rot_enum == 'xyz':
            row.prop(context.scene, 'camera_rot_xyz')
        else:
            row.prop(context.scene, 'camera_rot_quat')
        
        ########### The preview operator was here

        #Structured light
        row = layout.row()
        row.prop(context.scene, 'is_structured_light')

        if context.scene.is_structured_light:

            row = layout.row()
            row.label(text='Projector inputs', icon='LIGHT_SPOT')

            #Projector intrinsics
            row = layout.row()
            row.label(text='Intrinsic parameters', icon='LIGHT')

            row = layout.row()
            row.prop(context.scene, 'projector_focal_length')

            row = layout.row()
            row.prop(context.scene, 'projector_sensor_width')
            
            col = layout.column(align=True)
            
            row = col.row()
            row.prop(context.scene, 'projector_resolution_height')
            
            row = col.row()
            row.prop(context.scene, 'projector_resolution_width')


            #Projector extrinsics
            row = layout.row()
            row.label(text="Location (X, Y, Z)", icon='EMPTY_AXIS')

            row = layout.row()
            row.prop(context.scene, 'projector_loc_vec')

            row = layout.row()
            row.label(text='Rotation', icon='SPHERE')

            row = layout.row()
            row.prop(context.scene, 'projector_rot_enum')

            row = layout.row()
            if context.scene.projector_rot_enum == 'xyz':
                row.prop(context.scene, 'projector_rot_xyz')
            else:
                row.prop(context.scene, 'projector_rot_quat')
        
        row = layout.row()
        row.operator('datapipe.preview_camera_pose', icon='WORKSPACE')

        row = layout.row()
        row.operator('datapipe.append_camera_pose', icon='FILE_NEW')

            

'''
class DATAPIPE_PT_projector_panel(bpy.types.Panel):
    bl_idname = 'Projector_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DataPipe'
    bl_label = "Projector inputs"


    def draw(self, context):

        layout = self.layout

        layout.label(text="Projector inputs here")
'''

class DATAPIPE_PT_run_panel(bpy.types.Panel):
    bl_idname = 'Run_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DataPipe'
    bl_label = "Run pipeline"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.label(text="Enter path to save output:")

        row = layout.row()
        row.prop(context.scene, 'output_path')

        row = layout.row()
        row.operator('datapipe.run_pipeline', icon='PLAY')

        

classes = [
           DATAPIPE_PT_scenes_panel,
           DATAPIPE_PT_objects_panel,
           DATAPIPE_PT_camera_panel,
           DATAPIPE_PT_run_panel
          ]

def register():
    #################################
    ####### CAMERA PROPERTIES #######
    #################################
    bpy.types.Scene.camera_focal_length = bpy.props.FloatProperty(
        name='Focal length',
        unit='CAMERA')
    bpy.types.Scene.camera_sensor_width = bpy.props.FloatProperty(
        name='Sensor width',
        unit='CAMERA')
    bpy.types.Scene.camera_resolution_height = bpy.props.IntProperty(
        name='Resolution height',
        default= 480,
        subtype='PIXEL')
    bpy.types.Scene.camera_resolution_width = bpy.props.IntProperty(
        name='Resolution width',
        default= 720,
        subtype='PIXEL')
    bpy.types.Scene.camera_loc_vec = bpy.props.FloatVectorProperty(
        name='',
        unit='LENGTH')
    bpy.types.Scene.camera_rot_enum = bpy.props.EnumProperty(
        name='',
        items=[('xyz', 'XYZ Euler angles', ''),
               ('quat', 'Quaternions [w, x, y, z]', '')])
    bpy.types.Scene.camera_rot_xyz = bpy.props.FloatVectorProperty(
        name='',
        unit='ROTATION',
        min=0, 
        max=2*np.pi)
    bpy.types.Scene.camera_rot_quat = bpy.props.FloatVectorProperty(
        name='',
        default= [1,0,0,0],
        size=4)
    bpy.types.Scene.is_structured_light = bpy.props.BoolProperty(
        name='Structured light')
    
    ####################################
    ####### PROJECTOR PROPERTIES #######
    ####################################
    bpy.types.Scene.projector_focal_length = bpy.props.FloatProperty(
        name='Focal length',
        unit='CAMERA')
    bpy.types.Scene.projector_sensor_width = bpy.props.FloatProperty(
        name='Sensor width',
        unit='CAMERA')
    bpy.types.Scene.projector_resolution_height = bpy.props.IntProperty(
        name='Resolution height',
        default= 480,
        subtype='PIXEL')
    bpy.types.Scene.projector_resolution_width = bpy.props.IntProperty(
        name='Resolution width',
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
        default= (0, np.pi/180*8.5, 0),
        unit='ROTATION',
        min=0, 
        max=2*np.pi)
    bpy.types.Scene.projector_rot_quat = bpy.props.FloatVectorProperty(
        name='',
        default= (0.9972502, 0, 0.0741085, 0),
        size=4)
    
    ######################################
    ####### OUTPUT PATH PROPERTIES #######
    ######################################
    bpy.types.Scene.output_path = bpy.props.StringProperty(
        name='',
        subtype='DIR_PATH'
    )

    for cl in classes:
        bpy.utils.register_class(cl)

def unregister():
    #################################
    ####### CAMERA PROPERTIES #######
    #################################
    del bpy.types.Scene.camera_focal_length
    del bpy.types.Scene.camera_sensor_width
    del bpy.types.Scene.camera_resolution_height
    del bpy.types.Scene.camera_resolution_width
    del bpy.types.Scene.camera_loc_vec
    del bpy.types.Scene.camera_rot_enum
    del bpy.types.Scene.camera_rot_xyz
    del bpy.types.Scene.camera_rot_quat
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

    for cl in classes:
        bpy.utils.unregister_class(cl)

print("############ pipeline_panel End ############")