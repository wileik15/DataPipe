import bpy
from projector import Projector
import utility_fuctions
import random


class BlendCamera:

    def __init__(self, camera_name: str, config: dict):

        self.camera_config = config['camera']

        self.name = camera_name
        
        self.is_structured_light = self.camera_config["is_structured_light"]

        self.pose_list = self.camera_config["wrld2cam_pose_list"]

        self.blend_cam_obj = self.import_camera()

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

        return camera_obj
        


    def get_random_pose_from_list(self):
        """
        Selects a random pose from camera pose list.

        returns random pose.
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
        blend_obj = self.blend_cam_obj
        #Sample random pose from input list
        rand_pose = self.get_random_pose_from_list()
        rot_quat, transl = utility_fuctions.transformation_matrix_to_quat_and_translation(rand_pose)
        print("Blender object: {}".format(blend_obj.name))
        print("Rotation = {}\nTranslation = {}".format(rot_quat, transl))
        #Set blender camera objects position
        blend_obj.rotation_quaternion = rot_quat
        blend_obj.location = transl

