import bpy



class blendCamera:

    structured_light = True
    sensor_width = 36


    @classmethod
    def import_camera(cls):
        """
        Method for importing camera object in Blender scene

        :param structured_light: Determine if camera object is structured_light or structured light camera
        :type structured_light: Bool
        """

        bpy.ops.object.camera_add()
        cam = bpy.context.active_object
        cam.name = 'cam'
        bpy.data.cameras[cam.name].sensor_width = blendCamera.sensor_width

        if blendCamera.structured_light:
            print("Structured light is activated")

        else:
            print("Simple camera is activated")


if __name__ == '__main__':

    blendCamera.structured_light = True

    blendCamera.import_camera()