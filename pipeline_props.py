import bpy

class DATAPIPE_Properties(bpy.types.PropertyGroup):

    camera_loc: bpy.props.FloatVectorProperty(name='Location')

    camera_rot_type: bpy.props.EnumProperty(items=[('xyz', 'Use XYZ Euler angles', ''),
                                                    'quat', 'Use Quaternions', ''])
    


def register():

    bpy.utils.register_class(DATAPIPE_Properties)

    bpy.types.Scene.pipeline_props = bpy.props.PointerProperty(type=DATAPIPE_Properties)

def unregister():

    bpy.utils.unregister_class(DATAPIPE_Properties)

    del bpy.types.Scene.pipeline_props