import bpy
import random

class BlendScene:

    scene_num = 0
    finished_renders = 0

    def __init__(self, config: dict, camera: object):
        
        self.scene_number = self.get_scene_number()
        self.last_scene = False

        print("\nScenes in blend file: \n{}\n".format(list(bpy.data.scenes)))

        self.scene_config = config['scene']

        print("\n### Scene number {}".format(self.scene_number))

        self.total_num_renders = self.scene_config['num_renders']
        print("Total number of renders {}".format(self.total_num_renders))

        self.renders_for_scene = self.get_num_renders()
        print("Renders for this scene: {}".format(self.renders_for_scene))
    
    @classmethod
    def get_scene_number(cls):
        cls.scene_num +=1
        return cls.scene_num

    @classmethod
    def reset_scene_number(cls):
        cls.scene_num = 0

    @classmethod
    def set_finished_renders(cls, renders_for_scene: int):
        cls.finished_renders += renders_for_scene

    @classmethod
    def get_num_finished_renders(cls):
        return cls.finished_renders

    def get_num_renders(self):

        max_renders = self.scene_config['max_renders_per_scene']
        min_renders = self.scene_config['min_renders_per_scene']

        num_renders = random.randint(a=min_renders, b=max_renders)
        finished_renders = self.get_num_finished_renders()

        if finished_renders + num_renders >= self.total_num_renders:
            num_renders = self.total_num_renders - finished_renders

            self.last_scene = True
        
        self.set_finished_renders(num_renders)
        
        return num_renders



