import sys
import os
from pathlib import Path
import distutils.log
import distutils.dir_util
import open3d as o3d
import trimesh
import numpy as np

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from utils.io import FileFolders
from config import input_file, output_dir
from analysis.src.core import split
from calcification.src.geometry_tools import ply_to_leaflet

outputs = Path("/home/amir/projects/cardiovision/dev/cardiovision_results/cardiovision_results")

split(outputs)

distutils.log.set_verbosity(distutils.log.DEBUG)
distutils.dir_util.copy_tree(
    outputs,
    output_dir,
    update=1,
    verbose=0,
)

# sample = str(outputs/'calcium_left.ply')
sample = str(outputs/'valve_cusps'/'L_complete_cusps.ply'/'calcium_left.ply')

point_cloud = np.asarray(o3d.io.read_point_cloud(sample)) # Read the point cloud

# Separate the into points, colors and normals array
points = point_cloud[:,:3]
colors = point_cloud[:,3:6]
normals = point_cloud[:,6:]

# Initialize a point cloud object
pcd = o3d.geometry.PointCloud()
# Add the points, colors and normals as Vectors
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)
pcd.normals = o3d.utility.Vector3dVector(normals)

# Create a voxel grid from the point cloud with a voxel_size of 0.01
voxel_grid=o3d.geometry.VoxelGrid.create_from_point_cloud(pcd,voxel_size=0.01)

# Initialize a visualizer object
vis = o3d.visualization.Visualizer()
# Create a window, name it and scale it
vis.create_window(window_name='Bunny Visualize', width=800, height=600)

# Add the voxel grid to the visualizer
vis.add_geometry(voxel_grid)

# We run the visualizater
vis.run()
# Once the visualizer is closed destroy the window and clean up
vis.destroy_window()

