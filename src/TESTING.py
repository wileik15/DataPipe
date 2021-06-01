
import numpy as np
import math
import utility_fuctions
import random

l = ['this', 'list', 'will', 'be', 'poped']

index = random.randint(a=0, b = len(l)-1)
print("Index to pop: {}".format(index))
print("length of list before pop: {}".format(len(l)))
var = l.pop(index)
print("length of list after pop: {}".format(len(l)))
print('poped value: {}'.format(var))
print(l)


'''
def print_matrix(matrix):
    m = np.asarray(matrix)
    shape = matrix.shape
    if shape == (4,4):
        print("{:2.4f}, {:2.4f}, {:2.4f}, {:2.4f}\n{:2.4f}, {:2.4f}, {:2.4f}, {:2.4f}\n{:2.4f}, {:2.4f}, {:2.4f}, {:2.4f}\n{:2.4f}, {:2.4f}, {:2.4f}, {:2.4f}\n".format(m[0,0], m[0,1], m[0,2], m[0,3], 
                                                                                                                                                                       m[1,0], m[1,1], m[1,2], m[1,3],
                                                                                                                                                                       m[2,0], m[2,1], m[2,2], m[2,3],
                                                                                                                                                                       m[3,0], m[3,1], m[3,2], m[3,3]))
    elif shape == (3,3):
        print("{:6f}, {:6f}, {:6f}\n{:6f}, {:6f}, {:6f}\n{:6f}, {:6f}, {:6f}\n".format(m[0,0], m[0,1], m[0,2], m[1,0], m[1,1], m[1,2], m[2,0], m[2,1], m[2,2]))
    else:
        print("Matrix must be (3x3) or (4x4)")

xyz = np.array([2, -0.148353, 0])
quat = np.array([ 0.8391571, -0.040041, -0.0623601, 0.5388166])
rot = np.array([[ 0.9890159,  0.0000000, -0.1478094],
                [-0.1344027, -0.4161468, -0.8993096],
                [-0.0615104,  0.9092974, -0.4115758]])

xyz2 = np.array([1.2, 0, 1.573])
quat2 = np.array([0.582957, 0.3988224, -0.3997022, 0.5842431])
rot2 = np.array([[-0.0022037, -0.9999976, -0.0000000],
                 [0.3623569, -0.0007985, -0.9320391],
                 [0.9320368, -0.0020539,  0.3623578]])

xyz2rot, xyz2quat = utility_fuctions.xyz2rot(xyz2)
quat2rot = utility_fuctions.quat2rot(quat2)

xyz2quat2rot = utility_fuctions.quat2rot(xyz2quat)


print("\nxyz2rot")
print_matrix(xyz2rot)
print("Det = {}\n".format(np.linalg.det(xyz2rot)))

print("quat2rot")
print_matrix(quat2rot)
print("Det = {}\n".format(np.linalg.det(quat2rot)))

print("xyz2quat2rot")
print_matrix(xyz2quat2rot)
print("Det = {}\n".format(np.linalg.det(xyz2quat2rot)))

print("rot")
print_matrix(rot2)
print("Det = {}\n".format(np.linalg.det(rot2)))

'''