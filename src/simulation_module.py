import bpy
import time

from.objects_module import ObjectManager


class Simulation:

    def __init__(self, sim_end: int):

        self.sim_end = sim_end
        self.sim_start = 1
        
        bpy.context.scene.rigidbody_world.point_cache.frame_start = self.sim_start
        bpy.context.scene.frame_set(frame=self.sim_start)

        bpy.context.scene.rigidbody_world.point_cache.frame_end = self.sim_end
        bpy.context.scene.frame_end = self.sim_end

    
    def run_loop(self):
        sim_end = self.sim_end
        print("Simulation initiated")
        start = time.time()
        temp_prev = time.time()
        for frame_num in range(sim_end-2):
            bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1) #Loop frames to 400
            temp = time.time()
            print("\n--- FRAME {} at time {}s".format(frame_num+1, temp-temp_prev))
            temp_prev = temp
        end = time.time()
        print("Simulation done in {} seconds".format(end-start))


    def apply_simulated_transforms(self, object_manager: ObjectManager):

        for obj in object_manager.objects_in_scene:
            print("{}\nmatrix: {}\n".format(obj.name, obj.blend_ob.matrix_world))
            bpy.context.view_layer.objects.active = obj.blend_ob #Set obj to active
            bpy.ops.object.visual_transform_apply() #Apply transform
            print("New matrix: {}\n\n".format(obj.blend_ob.matrix_world))


