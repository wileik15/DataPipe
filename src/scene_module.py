import bpy
import random
from pathlib import Path

class BlendScene:

    scene_num = 0
    finished_renders = 0

    def __init__(self, config: dict, camera: object, object_importer: object):
        self.scene_config = config['scene']

        self.scene_number = self.get_scene_number()
        self.scene_name = "scene.{:04}".format(self.scene_num)

        print("### SCENE {} CREATED ###".format(self.scene_num))

        if self.scene_num == 1:
            Path(config['output']['path']).mkdir()

        self.drop_zone_location, self.drop_zone_dimensions = self.get_drop_zone_info(scene_config=self.scene_config)
        
        self.output_path = Path.joinpath(Path(config['output']['path']), self.scene_name)
        self.output_path.mkdir()

        self.last_scene = False

        self.total_num_renders = self.scene_config['num_renders']

        self.renders_for_scene = self.get_num_renders(camera=camera)

        self.object_importer = object_importer
    
    @classmethod
    def get_scene_number(cls):
        temp = cls.scene_num
        cls.scene_num += 1
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
    
    def get_drop_zone_info(self, scene_config: dict):

        if 'drop_zone' in bpy.data.objects.keys():
            
            drop_zone_ob = bpy.data.objects['drop_zone']
            bpy.ops.object.select_all(action='DESELECT')
            drop_zone_ob.select_get()
            bpy.ops.object.transform_apply(location=False, scale=True, rotation=False)

            drop_zone_loc = drop_zone_ob.location
            drop_zone_dim = drop_zone_ob.dimensions
            print("\n\nDrop zone info stored in scene object\nGathered from object\n- Location: {}\n- Dimensions: {}\n".format(drop_zone_loc,drop_zone_dim))
            
            bpy.data.objects.remove(drop_zone_ob, do_unlink=True)
            bpy.data.meshes.remove(bpy.data.meshes['drop_zone_mesh'], do_unlink=True)

        else:
            drop_zone_loc = list(scene_config['drop_zone_loc'])
            scale = scene_config['drop_zone_scale']
            drop_zone_dim = [2*scale[0], 2*scale[1], 2*scale[2]]
            print("\n\nDrop zone info stored in scene object\nGathered from config\n- Location: {}\n- Dimensions: {}\n".format(drop_zone_loc,drop_zone_dim))
        
        return list(drop_zone_loc), list(drop_zone_dim)
        

    def get_num_renders(self, camera: object):

        max_renders = self.scene_config['max_renders_per_scene']
        min_renders = self.scene_config['min_renders_per_scene']

        if max_renders > len(camera.pose_list):
            max_renders = len(camera.pose_list)

        num_renders = random.randint(a=min_renders, b=max_renders)
        finished_renders = self.get_num_finished_renders()

        if finished_renders + num_renders >= self.total_num_renders:
            num_renders = self.total_num_renders - finished_renders

            self.last_scene = True
        
        self.set_finished_renders(num_renders)
        
        return num_renders

    def print_elements_in_scene(self):
        print("\nObjects in scene {}:".format(self.scene_num))
        for obj in self.object_importer.objects_in_scene:

            print("Object: {}".format(obj.name))
            print("Filename: {}\n-----------------".format(obj.filename))



