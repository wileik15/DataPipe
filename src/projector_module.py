import bpy


class blendProjector:

    @staticmethod
    def add_collections_and_viewlayers():

        parent = bpy.context.scene.collection

        for shift in range(1,4):
            phase1_name = "p8s{}".format(shift)
            phase2_name = "p7s{}".format(shift)
            
            bpy.context.scene.view_layers.new(name=phase1_name)
            bpy.context.scene.view_layers.new(name=phase2_name)
            
            col1 = bpy.data.collections.new(name=phase1_name)
            col2 = bpy.data.collections.new(name=phase2_name)

            parent.children.link(col1)
            parent.children.link(col2)


if __name__ == '__main__':

    blendProjector.add_collections_and_viewlayers()