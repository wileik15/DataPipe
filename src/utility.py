import bpy
import sys
import subprocess

class versionControll:

    @staticmethod
    def blenderVersionCheck():
        """
        Verifies that Blender version 2.80 or later is installed
        """

        version = (bpy.app.version_string).split('.')

        if not (int(version[1]) >= 90):
            raise Exception("Blender version 2.80 or newer required.\n- Current version is Blender {}.{}.{}".format(version[0],version[1],version[2]))



class packageControll:

    @staticmethod
    def installDependencies(package_list):
        """
        installing package dependencies to Blenders bundled python
        """

        #Path to python executable
        py_exec = str(bpy.app.binary_path_python)

        #Ensure that pip is installed
        subprocess.call([py_exec, '-m', 'ensurepip', '--user'])

        #Install latest version of pip
        subprocess.call([py_exec, '-m', 'pip', 'install', '--upgrade', 'pip'])

        #Loop package list to install all of them
        for package_name in package_list:
            subprocess.check_call([py_exec, '-m', 'pip', 'install','{}'.format(package_name)])


if __name__ == '__main__':

    packageControll.installDependencies(["scipy"])