import bpy
import random

class BlendScene:

    prev_scene_num = 0
    finished_renders = 0
    last_scene = False

    def __init__(self, config: dict, camera: object):

        self.scene_config = config['scene']

        self.scene_num = self.iterate_scene_number()
        print("Scene number {}".format(self.scene_num))

        self.total_num_renders = self.scene_config['num_renders']
        print("Total number of renders {}".format(self.total_num_renders))
        self.renders_for_scene = self.get_num_renders()
        print("Renders for this scene: {}".format(self.total_num_renders))

    def iterate_scene_number(self):

        new_scene_num = self.prev_scene_num + 1
        self.prev_scene_num += 1

        return new_scene_num

    def get_num_renders(self):

        max_renders = self.scene_config['max_renders_per_scene']
        min_renders = self.scene_config['min_renders_per_scene']

        renders = random.randint(a=min_renders, b=max_renders)

        if self.finished_renders + renders >= self.total_num_renders:
            renders = self.total_num_renders - self.finished_renders

            self.last_scene = True
        
        self.finished_renders += renders
        
        return renders



