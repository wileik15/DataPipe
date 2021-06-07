import bpy
import numpy as np
import random
import copy

from .projector_module import Projector


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
            self.pattern_generator = self.projector.pattern_generator

        self.K = self.get_calibration_matrix_K_from_blender(mode='complete')


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


    def get_calibration_matrix_K_from_blender(self, mode='complete'):

        scene = bpy.context.scene

        scale = scene.render.resolution_percentage / 100
        width = scene.render.resolution_x * scale # px
        height = scene.render.resolution_y * scale # px

        camdata = scene.camera.data

        if mode == 'simple':

            aspect_ratio = width / height
            K = np.zeros((3,3), dtype=np.float32)
            K[0][0] = width / 2 / np.tan(camdata.angle / 2)
            K[1][1] = height / 2. / np.tan(camdata.angle / 2) * aspect_ratio
            K[0][2] = width / 2.
            K[1][2] = height / 2.
            K[2][2] = 1.
            K.transpose()
        
        if mode == 'complete':

            focal = camdata.lens # mm
            sensor_width = camdata.sensor_width # mm
            sensor_height = camdata.sensor_height # mm
            pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

            if (camdata.sensor_fit == 'VERTICAL'):
                # the sensor height is fixed (sensor fit is horizontal), 
                # the sensor width is effectively changed with the pixel aspect ratio
                s_u = width / sensor_width / pixel_aspect_ratio 
                s_v = height / sensor_height
            else: # 'HORIZONTAL' and 'AUTO'
                # the sensor width is fixed (sensor fit is horizontal), 
                # the sensor height is effectively changed with the pixel aspect ratio
                pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
                s_u = width / sensor_width
                s_v = height * pixel_aspect_ratio / sensor_height

            # parameters of intrinsic calibration matrix K
            alpha_u = focal * s_u
            alpha_v = focal * s_v
            u_0 = width / 2
            v_0 = height / 2
            skew = 0 # only use rectangular pixels

            K = np.array([
                [alpha_u,    skew, u_0],
                [      0, alpha_v, v_0],
                [      0,       0,   1]
            ], dtype=np.float32)
        
        return K