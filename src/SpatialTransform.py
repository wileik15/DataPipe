import numpy as np
from scipy.spatial.transform import Rotation


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


def pose_to_tranformation_matrix(quaternions, location):
    """
    Changes Blenders quaternion representation and location
    to transformation matrix representation
    """
    R = quat2rot(quat=quaternions)
    t = location

    T = np.array([[R[0,0], R[0,1], R[0,2], t[0]],
                    [R[1,0], R[1,1], R[1,2], t[1]],
                    [R[2,0], R[2,1], R[2,2], t[2]],
                    [0,      0,      0,      1   ]])
    return T, R, t


def transformation_matrix_to_quat_and_translation(matrix):
    """
    Converts pose from transformation matrix format to quaternions and translation
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