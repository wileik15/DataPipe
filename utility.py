import bpy
import sys
import subprocess

class versionControll:

    def blenderVersionCheck():
        """
        Verifies that Blender version 2.80 or later is installed
        """

        version = (bpy.app.version_string).split('.')

        if not (int(version[1]) >= 80):
            raise Exception("Blender version 2.80 or newer must be installed. Current version Blender {}.{}.{}".format(version[0],version[1],version[2]))

class packageControll:

    def installDependencies(package_list):

        for package_name in package_list:
            subprocess.check_call([sys.executable, '-m', 'install','{}'.format(package_name)])
