import bpy
from .projector import Projector
import random


class BlendCamera:

    def __init__(self, camera_name: str, config: dict):
        print("### Camera object created ###")

        self.camera_config = config['camera']

        self.name = camera_name
        
        self.is_structured_light = self.camera_config["is_structured_light"]
        self.pose_list = self.camera_config["wrld2cam_pose_list"]

        self.blend_cam_obj, self.blend_cam_data = self.import_camera()

        if self.is_structured_light:
            self.projector = Projector(self, config=config)
        
        #Move to first pose
        self.move()
        


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
        


    def get_random_pose_from_list(self):
        """
        Selects a random pose from camera pose list.

        Returns random tansformation numpy matrix.
        """
        
        poses = self.pose_list

        #Pick random index of pose list
        index = random.randint(a=0, b=len(poses)-1)
        print("Camera random pos: {}".format(poses[index]))

        return poses[index]
    
    def move(self):
        """
        moves camera object to random position.
        """
        print("\n###### MOVING CAMERA ######")

        #Sample random pose from input list
        rand_pose = self.get_random_pose_from_list()
        
        self.blend_cam_obj.location = rand_pose['location']
        self.blend_cam_obj.rotation_quaternion = rand_pose['rotation']
        
        print("in move() ---> Blender object: {}".format(self.blend_cam_obj.name))

        print("in move() ---> Rotation = {}\nTranslation = {}\n".format(self.blend_cam_obj.rotation_quaternion, self.blend_cam_obj.location))

