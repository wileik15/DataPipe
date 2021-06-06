import bpy
from .projector_module import Projector
import random
import copy


class BlendCamera:

    def __init__(self, camera_name: str, config: dict):
        print("### Camera object created ###")

        self.camera_config = config['camera']

        self.name = camera_name
        
        self.is_structured_light = self.camera_config["is_structured_light"]
        
        self.pose_list = self.camera_config["wrld2cam_pose_list"]
        self.pose_list_copy = copy.copy(self.pose_list)

        self.blend_cam_obj, self.blend_cam_data = self.import_camera()

        bpy.context.scene.camera = self.blend_cam_obj

        if self.is_structured_light:
            self.projector = Projector(self, config=config)
            self.pattern_names = self.projector.pattern_names_list


    def import_camera(self):
        """
        Imports camera into blender scene.
        """
        camera = bpy.data.cameras.new(name=self.name)
        camera_obj = bpy.data.objects.new(name=self.name, object_data=camera)
        
        parent_col = bpy.context.scene.collection
        parent_col.objects.link(camera_obj)

        camera_obj.rotation_mode = 'QUATERNION'

        return camera_obj, camera
        


    def get_random_pose_from_list(self, curr_render: int):
        """
        Selects a random pose from camera pose list.

        Returns random tansformation numpy matrix.
        """
        if curr_render == 1:
            print("\n-- New render sequence --")
            self.pose_list_copy = copy.copy(self.pose_list)

        #Pick random index of pose list
        index = random.randint(a=0, b=len(self.pose_list_copy)-1)

        print("Unique camera poses left: {}".format(len(self.pose_list_copy)))
        pose = self.pose_list_copy.pop(index)

        print("Camera random pos: {}".format(pose))

        return pose
    
    def move(self, curr_render: int):
        """
        moves camera object to random position.
        """
        print("\n###### MOVING CAMERA ######")

        #Sample random pose from input list
        print("\n------------\n")
        rand_pose = self.get_random_pose_from_list(curr_render=curr_render)
        print("\n------------\n")
        
        self.blend_cam_obj.location = rand_pose['location']
        self.blend_cam_obj.rotation_quaternion = rand_pose['rotation']

        bpy.context.view_layer.objects.active = self.blend_cam_obj
        bpy.ops.object.visual_transform_apply()
        
        print("in move() ---> Blender object: {}".format(self.blend_cam_obj.name))

        print("in move() ---> Rotation = {}\nTranslation = {}\n".format(self.blend_cam_obj.rotation_quaternion, self.blend_cam_obj.location))

