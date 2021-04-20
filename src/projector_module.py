import bpy
from numpy import pi


class BlendProjector:
    """
    Projector class for Blender
    """

    shifts = 3

    @staticmethod
    def add_collections_and_viewlayers():
        """
        sdads
        """

        #Set parent collection to be scene master collection
        parent = bpy.context.scene.collection

        #Loop number of phase shifts in structured light algorithm
        for shift in range(0,BlendProjector.shifts):
            #Pattern name for both wave lengths at current shift
            pattern1_name = "p1s{}".format(shift+1)
            pattern2_name = "p2s{}".format(shift+1)
            
            #Create viewlayers for both wave lengths at current shift
            bpy.context.scene.view_layers.new(name=pattern1_name)
            bpy.context.scene.view_layers.new(name=pattern2_name)
            
            #Create collections for both wave lengths at current shift
            col1 = bpy.data.collections.new(name=pattern1_name)
            col2 = bpy.data.collections.new(name=pattern2_name)

            #Make collections children of master collection/scene collection
            parent.children.link(col1)
            parent.children.link(col2)

    @staticmethod
    def add_light_source():
        #Add spotlight
        bpy.ops.object.light_add(type='SPOT')
        spot = bpy.context.active_object

        #Lock spotlight pose relative to camera pose
        cam = bpy.data.objects['cam']
        spot.parent = cam
        spot.parent_type = 'OBJECT'
        spot.location = (-0.15, 0, 0)
        spot.rotation_euler = (0, 8.5, 0)


    @staticmethod
    def print_collection_names():

        collections = bpy.data.collections

        for collection in collections:

            print("\n-------------------\nCollection\nName: {}\nChildren: {}\nObjects in: {}\n-------------------".format(collection.name, (collection.children), collection.objects))


if __name__ == '__main__':

    BlendProjector.add_collections_and_viewlayers()

    BlendProjector.print_collection_names()

    BlendProjector.add_light_source()
'''
x_scale = focal_length/sensorwidth_x
y_scale = (focal_length/sensorwidth_x)*(res_y/res_x)
'''