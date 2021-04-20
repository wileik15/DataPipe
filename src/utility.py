import os
import json
import sys
import bpy
import subprocess
import numpy as np
from scipy.spatial.transform import Rotation

class VersionControll:

    @staticmethod
    def blenderVersionCheck():
        """
        Verifies that Blender version 2.80 or later is installed
        """

        version = (bpy.app.version_string).split('.')

        if not (int(version[1]) >= 90):
            raise Exception("Blender version 2.80 or newer required.\n- Current version is Blender {}.{}.{}".format(version[0],version[1],version[2]))



class PackageControll:

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



class SpatialTransforms:

    @staticmethod
    def quat2rot(quat):
        """
        Converts blender quaternion representation to rotation matrix

        :param: quat
        :type quat: array
        """
        #Converts from blender quaternion representation
        q = [quat[1], quat[2], quat[3], quat[0]]

        quat = Rotation.from_quat(q) #Stores as a rotation
        R = quat.as_matrix() #Rotation matrix
        return R

    @staticmethod
    def rot2quat(rot):
        """
        Converts a rotation matrix to  blender quaternion representation

        :param: rot
        :type rot: array
        """
        R = Rotation.from_matrix(rot) #Stores as a rotation
        q = R.as_quat() #Quaternions

        quat = [q[3], q[0], q[1], q[2]] #Saves quaternion in Blender representation
        return quat

'''

    @staticmethod
    def pose_to_tranformation_matrix(quaternions, location):
        """
        Changes Blenders quaternion representation and location
        to transformation matrix representation
        """
        R = poseUtility.quat_to_rot(quaternions)
        t = location

        T = np.array([[R[0,0], R[0,1], R[0,2], t[0]],
                      [R[1,0], R[1,1], R[1,2], t[1]],
                      [R[2,0], R[2,1], R[2,2], t[2]],
                      [0,      0,      0,      1   ]])
        return T, R, t

    @staticmethod
    def transform_inverse(matrix):
        R = matrix[0:3, 0:3]
        t = matrix[0:3, 3]

        T = np.zeros_like(matrix)
        T[0:3, 0:3] = np.transpose(R)
        T[0:3, 3] = - np.transpose(R)@t
        T[3,3] = 1
        return T
    
    @staticmethod
    def cam2obj_transform(obj, cam_pos_matrix):
        obj_translation = obj.location #Get object location vector
        obj_quaternions = obj.rotation_quaternion #Get object rotation on quaternion
        obj_trans_quaternions = poseUtility.rot_to_quat(poseUtility.quat_to_rot(obj_quaternions))

        cam_translation = cam_pos_matrix[0:3,3] #Get camera location vector
        cam_quaternions = poseUtility.rot_to_quat(cam_pos_matrix[0:3,0:3]) #Get camera rotation on quaternion

        T_so, R_so, t_so = poseUtility.pose_to_tranformation_matrix(obj_quaternions, obj_translation) #Object transformation matrix in world coordinates
        T_sc, R_sc, t_sc = poseUtility.pose_to_tranformation_matrix(cam_quaternions, cam_translation) #Camera transformation matrix in world coordinates

        T_cs = poseUtility.transform_inverse(T_sc) #World coordinate system in camera coordinate system

        T_co = np.matmul(T_cs,T_so) #Object transform from camera coordinate system
        R_co = T_co[0:3,0:3] #Rotation
        t_co = T_co[0:3,3] #Translation

        return T_co, R_co, t_co
'''



if __name__ == '__main__':

    PackageControll.installDependencies(["scipy"])