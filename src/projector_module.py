import bpy


class projector:

    @staticmethod
    def add_collections_and_viewlayers():
        
        for phase in range(1,4,1):
            phase1_name = "p{}_l{}".format(phase, 8)
            phase2_name = "p{}_l{}".format(phase, 7)

            bpy.context.scene.view_layers.new(name=phase1_name)
            bpy.context.scene.view_layers.new(name=phase2_name)

            bpy.data.collections.new(name=phase1_name)
            bpy.data.collections.new(name=phase2_name)