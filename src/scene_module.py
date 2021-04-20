import bpy

class BlendScene:

    @staticmethod
    def set_up_scene():
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.device = 'GPU'

        bpy.context.scene.unit_settings.system = 'METRIC'
        bpy.context.scene.unit_settings.length_unit = 'METERS'
        bpy.context.scene.unit_settings.system_rotation = 'DEGREES'


BlendScene.set_up_scene()