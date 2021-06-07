from genericpath import exists
import types
import bpy
import subprocess
import numpy as np
from scipy.spatial.transform import Rotation
import os
from pathlib import Path

from .scene_module import BlendScene
from .config_module import input_storage

class PathUtility:

    @staticmethod
    def get_addon_path():
        """
        Returns path to addon folder.
        """
        resource_path = Path(bpy.utils.resource_path(type='USER'))
        addon_sub_path = Path("scripts/addons/DataPipe")
        addon_path = Path.joinpath(resource_path, addon_sub_path)
        print("addon_path:\n{}".format(addon_path))
        return str(addon_path)

    @staticmethod
    def get_patterns_path():
        """
        Returns path to patterns folder.
        """
        resource_path = Path(bpy.utils.resource_path(type='USER'))
        pattern_sub_path = Path("scripts/addons/DataPipe/utility/SL_patterns")
        pattern_path = Path.joinpath(resource_path, pattern_sub_path)
        print("$$$$$$$\nResource path:\n{}\n--> Type: {}\n\nPattern sub path:\n{}\n--> Type: {}\n\nTotal path:\n{}\n--> Type: {}\n$$$$$$$".format(resource_path, type(resource_path), pattern_sub_path, type(pattern_sub_path), pattern_path, type(pattern_path)))
        return str(pattern_path)
    
    @staticmethod
    def get_pipeline_run_output_path(path: Path):
        path = Path(bpy.path.abspath(path)).resolve()
        dir_name = Path("DataPipe_run")
        out_path = Path.joinpath(path,dir_name)
        print("Try 1 at path_\n{}".format(str(out_path)))
        if not os.path.exists(out_path):
            return str(out_path)

        exists = True
        index = 1

        while exists:
            dir_name = 'DataPipe_run.{:04d}'.format(index)
            out_path = Path.joinpath(path, dir_name)
            print("Try {} at path:\n{}".format(index+1, str(out_path)))
            if not Path.exists(out_path):
                exists = False
                return str(out_path)
            index += 1
        



class PackageControll:
    """
    Class for installing python dependencies for the pipeline addonq
    """

    package_list = ["opencv-python", "scipy"]

    @classmethod
    def installDependencies(cls):
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
        for package_name in cls.package_list:
            subprocess.check_call([py_exec, '-m', 'pip', 'install','{}'.format(package_name)])



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

def xyz2rot(xyz):

    xyz_rot = Rotation.from_euler(seq='XYZ',angles=xyz)
    R = xyz_rot.as_matrix()
    q = xyz_rot.as_quat()
    quat = np.array([q[3], q[0], q[1], q[2]])
    return R, quat

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



def pose_to_tranformation_matrix(rotation, location):
    """
    Changes Blenders quaternion or Euler rotational representation and location
    to transformation matrix representation
    """

    if len(rotation) == 4:
        R = quat2rot(quat=rotation)
    else:
        R = xyz2rot(xyz= rotation)

    t = location

    T = np.array([[R[0,0], R[0,1], R[0,2], t[0]],
                  [R[1,0], R[1,1], R[1,2], t[1]],
                  [R[2,0], R[2,1], R[2,2], t[2]],
                  [0,      0,      0,      1   ]])
    return T, R, t


def transformation_matrix_to_quat_and_translation(matrix):
    """
    Converts pose from transformation matrix format to quaternions and translation

    return: [quaternions] and [x,y,z]
    """
    quat = rot2quat(rot=matrix[0:3,0:3])
    trans = [matrix[0,3], matrix[1,3], matrix[2,3]]
    return quat, trans


def transform_inverse(matrix):
    R = matrix[0:3, 0:3]
    t = matrix[0:3, 3]

    T = np.zeros_like(matrix)
    T[0:3, 0:3] = np.transpose(R)
    T[0:3, 3] = - np.transpose(R)@t
    T[3,3] = 1
    return T


def cam2obj_transform(blender_object, cam_pos_matrix):
    obj_translation = blender_object.location #Get object location vector
    obj_quaternions = blender_object.rotation_quaternion #Get object rotation on quaternion
    obj_trans_quaternions = rot2quat(quat2rot(obj_quaternions))

    cam_translation = cam_pos_matrix[0:3,3] #Get camera location vector
    cam_quaternions = rot2quat(cam_pos_matrix[0:3,0:3]) #Get camera rotation on quaternion

    T_so, R_so, t_so = pose_to_tranformation_matrix(obj_quaternions, obj_translation) #Object transformation matrix in world coordinates
    T_sc, R_sc, t_sc = pose_to_tranformation_matrix(cam_quaternions, cam_translation) #Camera transformation matrix in world coordinates

    T_cs = transform_inverse(T_sc) #World coordinate system in camera coordinate system

    T_co = np.matmul(T_cs,T_so) #Object transform from camera coordinate system
    R_co = T_co[0:3,0:3] #Rotation
    t_co = T_co[0:3,3] #Translation

    return T_co, R_co, t_co

def file_exists(file_path: str):

    return os.path.exists(file_path)


def initialize_pipeline_environment():
    """
    Setting blender variables to the required specifications for the pipeline.
    -Rendering engine is set to cycles and gpu-compute.
    -Scene units are set to metric.
    -Native object
    """
    print("###### INITIALIZING PIPELINE ######")

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'

    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.length_unit = 'METERS'
    bpy.context.scene.unit_settings.system_rotation = 'RADIANS'
    bpy.context.scene.unit_settings.mass_unit = 'KILOGRAMS'
    bpy.context.scene.world.color = (0,0,0)

    BlendScene.reset_scene_number()
    input_storage.reset_config_dict()


    #Make all existing meshes be rigid bodies.
    for obj in bpy.data.objects:
        print("---------")
        print("Object name {}".format(obj.name))
        print("Object type {}".format(type(obj)))

        obj.pass_index = 0
        
        bpy.context.view_layer.objects.active = obj
        print("Object type: {}".format(str(bpy.context.object.type)))
        if bpy.context.object.type == 'MESH':
            bpy.ops.rigidbody.object_add(type='PASSIVE')
            bpy.context.object.rigid_body.collision_shape = 'MESH'


            obj.rigid_body.collision_margin = 0.001