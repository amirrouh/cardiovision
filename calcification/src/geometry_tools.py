# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 16:01:00 2022

@author: rz445
"""

import numpy as np
import open3d as o3d
import trimesh
import vtk
from scipy.ndimage import binary_fill_holes

def create_stl(nrrd_dir,stl_dir):
    
    """Creates .stl from .nrrd
    
    :param ply_path: .nrrd directory
    :type ply_path: string
    :param stl_path: .stl directory
    :type stl_path: string
    
    """

    #Read information from nrrd
    reader = vtk.vtkNrrdReader()
    reader.SetFileName(nrrd_dir)
    reader.Update()
    
    #Implements marching cube operation
    dmc = vtk.vtkDiscreteMarchingCubes()
    dmc.SetInputConnection(reader.GetOutputPort())
    dmc.GenerateValues(1, 1, 1)
    dmc.Update()
    
    smoothFilter = vtk.vtkSmoothPolyDataFilter()
    smoothFilter.SetNumberOfIterations(300)
    smoothFilter.SetRelaxationFactor(0.1);
    smoothFilter.FeatureEdgeSmoothingOff();
    smoothFilter.BoundarySmoothingOn();
    smoothFilter.SetInputConnection(dmc.GetOutputPort())
    smoothFilter.Update()
    
    #Write .stl
    writer = vtk.vtkSTLWriter()
    writer.SetInputConnection(smoothFilter.GetOutputPort())
    writer.SetFileTypeToBinary()
    writer.SetFileName(stl_dir)
    writer.Write()

    return

def ply_to_voxels(ply_path,alpha,pitch,multi_factor):
    
    """Converts .ply file to NumPy array
    
    :param ply_path: .ply directory
    :type ply_path: string
    :param alpha: alpha value used to create mesh
    :type alpha: int/float
    :param pitch: Used in voxelisation procedure. Smaller the value, more voxels for every point
    :type pitch: int/float
    :param multi_factor: The interpolation factor used to increase the size of the .ply file
    :type multi_factor: int/float
    
    :return mat: 3D array of the leaflet
    :rtype: 3D NumPy array
    :return xyz: Array of the points from the .ply
    :rtype: NumPy array
    """

    # visit http://www.open3d.org/docs/latest/tutorial/Advanced/surface_reconstruction.html
    # for more information
    pcd = o3d.io.read_point_cloud(ply_path) # Read the point cloud
    pcd.estimate_normals()
    rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha)
    rec_mesh.scale(multi_factor, center=(0, 0, 0))
    rec_mesh.compute_vertex_normals()   
    tri_mesh = trimesh.Trimesh(np.asarray(rec_mesh.vertices), np.asarray(rec_mesh.triangles),
                              vertex_normals=np.asarray(rec_mesh.vertex_normals))
    trimesh.convex.is_convex(tri_mesh)
    volume = tri_mesh.voxelized(pitch=pitch) #Voxelize points
    mat = volume.matrix # point cloud to voxelized data

    xyz = np.asarray(pcd.points) #x,y and physical points
    
    return mat , xyz

def ply_to_leaflet(ply_path,alpha,pitch,multi_factor,raw_arr):
    
    """Converts .ply file to NumPy array with correct physical space
    
    :param mat: .ply directory
    :type mat: string
    :type alpha: int/float
    :param pitch: Used in voxelisation procedure. Smaller the value, more voxels for every point
    :type pitch: int/float
    :param multi_factor: The interpolation factor used to increase the size of the .ply file
    :type multi_factor: int/float
    :param raw_arr: The NumPy array that comes from the .nnrd image. Used to match NumPy shape
    :type raw_arr: 3D NumPy array
    
    :return mat_filled: 3D array of the leaflet adjusted to match the .nrrd file
    :rtype: 3D NumPy array

    """

    leaflet_voxels,leaflet_points=ply_to_voxels(ply_path,alpha,pitch,multi_factor)
    leaflet_numpy=position_leaflet(leaflet_voxels,leaflet_points,raw_arr,multi_factor)
    
    return np.array(leaflet_numpy)

def position_leaflet(mat,points,raw_arr,multi_factor):
    
    x=points[:,0]
    y=points[:,1]
    z=points[:,2]
    
    #The coordinate system of the .ply and the .nrrd are different.
    #We have to match both of them so they share the same physical space
    #We determine the necessary buffer to center the valve correctly
    
    #Lower buffer (at the min of the x,y and coordinates)
    x_lower_buffer = np.zeros((int(round(multi_factor*np.min(x))),np.shape(mat)[1],np.shape(mat)[2]))
    mat=np.vstack((x_lower_buffer,mat)) #Append adjustment
    y_lower_buffer = np.zeros((np.shape(mat)[0],int(round(multi_factor*np.min(y))),np.shape(mat)[2]))
    mat=np.hstack((y_lower_buffer,mat))
    z_lower_buffer = np.zeros((np.shape(mat)[0],np.shape(mat)[1],int(multi_factor*round(np.min(z)))))
    mat=np.dstack((z_lower_buffer,mat))
    
    raw_shape=np.shape(raw_arr)
    
    #Upper buffer (at the max of the x,y and coordinates)
    x_upper_buffer = np.zeros((raw_shape[0]-np.shape(mat)[0],np.shape(mat)[1],np.shape(mat)[2]))
    mat=np.vstack((mat,x_upper_buffer))
    y_upper_buffer = np.zeros((np.shape(mat)[0],raw_shape[1]-np.shape(mat)[1], np.shape(mat)[2]))
    mat=np.hstack((mat,y_upper_buffer))
    z_upper_buffer = np.zeros((np.shape(mat)[0],np.shape(mat)[1],raw_shape[2]-np.shape(mat)[2]))
    mat=np.dstack((mat,z_upper_buffer))
    
    #The valve now occupies the correct physical space
    
    #Fill in the valve so it is not hollow
    mat_filled=binary_fill_holes(mat).astype(int)
    
    return mat_filled

def ply_to_stl(ply_path,stl_path,alpha):
    """Creates .stl from .ply using alpha shape function
      visit http://www.open3d.org/docs/latest/tutorial/Advanced/surface_reconstruction.html
      for more information
    
    :param ply_path: .ply directory
    :type ply_path: string
    :param stl_path: .stl directory
    :type stl_path: string
    
    """
    
    # visit http://www.open3d.org/docs/latest/tutorial/Advanced/surface_reconstruction.html
    # for more information
    pcd = o3d.io.read_point_cloud(ply_path) # Read the point cloud
    pcd.estimate_normals()
    rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha)
    rec_mesh.compute_vertex_normals()   
    tri_mesh = trimesh.Trimesh(np.asarray(rec_mesh.vertices), np.asarray(rec_mesh.triangles),
                              vertex_normals=np.asarray(rec_mesh.vertex_normals))
    trimesh.convex.is_convex(tri_mesh)
    tri_mesh.export(stl_path)
    
    return