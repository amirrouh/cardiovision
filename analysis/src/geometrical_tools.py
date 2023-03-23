from pathlib import Path
import open3d as o3d
import numpy as np
import pandas as pd
from stl import mesh
import trimesh
import pyntcloud
from scipy.spatial import Delaunay
from plyfile import PlyData
from tqdm import tqdm
import shutil
import plyfile
from scipy.spatial import ConvexHull


def ply_to_stl(ply_path:Path,stl_path:Path,alpha):
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
    pcd = o3d.io.read_point_cloud(str(ply_path)) # Read the point cloud
    pcd.estimate_normals()
    rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha)
    rec_mesh.compute_vertex_normals()   
    tri_mesh = trimesh.Trimesh(np.asarray(rec_mesh.vertices), np.asarray(rec_mesh.triangles),
                              vertex_normals=np.asarray(rec_mesh.vertex_normals))
    trimesh.convex.is_convex(tri_mesh)
    tri_mesh.export(str(stl_path))
    
def stl2ply(stl_file: Path, ply_file: Path, samples: int = 500):
    """ Convert STL file to PLY
    Args:
        stl_file (Path): input path
        ply_file (Path): putput path
        samples (int): number of points to form the point cloud from mesh, the higher sample,
        the more accurate shape of the pointcloud
    """
    o3d.obj = o3d.io.read_triangle_mesh(str(stl_file))
    arr = np.asarray(o3d.obj)
    pcd = o3d.obj.sample_points_uniformly(samples)
    o3d.io.write_point_cloud(
        str(ply_file), pcd)
    

def get_stl_volume(stl_path):
    # Load the STL file
    stl_file = mesh.Mesh.from_file(stl_path)
    # Calculate the volume of the mesh
    volume, _, _ = stl_file.get_mass_properties()
    return volume


def detect_islands_stl(input_stl_file: Path, output_dir: Path):
    # Load the STL file
    mesh = trimesh.load_mesh(str(input_stl_file))

    # Get the connected components
    components = mesh.split(only_watertight=True)

    # Iterate over the connected components
    for i, component in enumerate(components):
        # Save the component as a separate STL file
        component.export(str(output_dir/'component_{}.stl'.format(i)))




def detect_islands_ply(input_ply_file: str, output_dir: Path):
    import open3d as o3d

    # Load the PLY file
    pcd = o3d.io.read_point_cloud(input_ply_file)

    # Compute the normals of the point cloud
    pcd.estimate_normals()

    # Convert the point cloud to a triangle mesh
    mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd)

    # Compute the normals of the mesh
    mesh.compute_vertex_normals()

    # Check for disconnected parts
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()
    labels = mesh.cluster_connected_triangles()

    print(labels)

    # Select each island and export it as an STL file
    for i in range(max(labels)+1):
        island = mesh.select_by_index(np.where(labels == i)[0])
        o3d.io.write_triangle_mesh(str(output_dir / f"island_{i}.stl"), island)




def combine_ply_files(ply_files: list, saveto_path: Path):

    clouds = []
    for f in ply_files:
        clouds.append(pyntcloud.PyntCloud.from_file(str(f)))

    # Concatenate the points of the three clouds
    combined_points = pd.concat([i.points for i in clouds])

    # Create a new PyntCloud object with the combined points
    combined_cloud = pyntcloud.PyntCloud(points=combined_points)

    # Save the combined cloud to a PLY file
    combined_cloud.to_file(str(saveto_path))


def intersection(file1, file2):
    """Detect the intersectin between two PLY files
    Args:
        file1 (Path): _description_
        file2 (Path): _description_
    Returns:
        array: Intersected coordinates
    """

    # Load the first ply file
    ply1 = PlyData.read(str(file1))

    # Load the second ply file
    ply2 = PlyData.read(str(file2))

    # Extract the vertex coordinates of the first ply file
    vertex_data1 = np.vstack(
        [ply1['vertex']['x'], ply1['vertex']['y'], ply1['vertex']['z']]).T

    # Extract the vertex coordinates of the second ply file
    vertex_data2 = np.vstack(
        [ply2['vertex']['x'], ply2['vertex']['y'], ply2['vertex']['z']]).T

    # Create a Delaunay triangulation of the first ply file's vertices
    tri = Delaunay(vertex_data1)

    # Find the indices of the vertices of the second ply file that are inside the triangulation
    intersection_indices = tri.find_simplex(vertex_data2) >= 0

    # Extract the vertex coordinates of the intersection
    intersection = vertex_data2[intersection_indices]

    return intersection


def keep_intersected_islands(reference_cloud: Path, islands_path: Path, saveto_path: str):
    islands = islands_path.rglob("*.ply")
    for island in tqdm(islands, desc="Detecting aortic valve calcium regions..."):
        intsct = intersection(reference_cloud, island)
        if intsct.size > 0:
            shutil.copy(island, saveto_path/island.name)

        
def split(cv_results_path: Path):

    cusps = list(cv_results_path.rglob("*cusp.ply"))
    calcium_file = cv_results_path/"calcs_corr.stl"

    print(cv_results_path)

    right_cusp = np.asarray(o3d.io.read_triangle_mesh(str(cusps[0])))
    left_cusp = np.asarray(o3d.io.read_triangle_mesh(str(cusps[1])))
    non_cusp = np.asarray(o3d.io.read_triangle_mesh(str(cusps[2])))

    calcium = np.asarray(o3d.io.read_triangle_mesh(str(calcium_file)).vertices)
    landmarks = pd.read_csv(cv_results_path/"landmarks.csv", header=None)

    calcium_stl = np.asarray(o3d.io.read_triangle_mesh(str(calcium_file)))

    center = landmarks.mean().values
    center[2] = landmarks.iloc[5][2]

    landmarks = np.array(landmarks)

    top_landmarks = landmarks[:3, :2]
    bottom_landmarks = landmarks[3:-1, :2]

    top_angels = []
    for landmark in top_landmarks:
        angel = np.rad2deg(np.arctan2(
            landmark[1]-center[1], landmark[0]-center[0]))
        top_angels.append(angel)
    bottom_angels = []
    for landmark in bottom_landmarks:
        angel = np.rad2deg(np.arctan2(
            landmark[1]-center[1], landmark[0]-center[0]))
        if angel < 0:
            angel += 360
        bottom_angels.append(angel)

    calcium_right = []
    calcium_left = []
    calcium_none = []

    counter = 0
    for point in calcium:
        angel = np.rad2deg(np.arctan2(point[1]-center[1], point[0]-center[0]))
        if angel < 0:
            angel += 360
        counter += 1
        targets = []

        # Left cusp
        if bottom_angels[0] < bottom_angels[1]:
            if bottom_angels[0] <= angel <= bottom_angels[1]:
                targets.append("left")
        else:
            if bottom_angels[1] <= angel <= bottom_angels[0]:
                targets.append("left")

        # None cusp
        if bottom_angels[1] < bottom_angels[2]:
            if bottom_angels[1] <= angel <= bottom_angels[2]:
                targets.append("none")
        else:
            if bottom_angels[2] <= angel <= bottom_angels[1]:
                targets.append("none")

        # Right cusp
        if bottom_angels[0] < bottom_angels[2]:
            if bottom_angels[0] <= angel <= bottom_angels[2]:
                targets.append("right")
        else:
            if angel <= bottom_angels[2]:
                targets.append("right")

        if "left" in targets:
            calcium_left.append(point)
        elif "right" in targets:
            calcium_right.append(point)
        elif "none" in targets:
            calcium_none.append(point)

    calcium_right_pcd = o3d.geometry.PointCloud()
    calcium_right_pcd.points = o3d.utility.Vector3dVector(calcium_right)
    try:
        o3d.io.write_point_cloud(
            str(cv_results_path / "calcium_right.ply"), calcium_right_pcd)
    except:
        print("There is no calcium on the right cusp")

    calcium_left_pcd = o3d.geometry.PointCloud()
    calcium_left_pcd.points = o3d.utility.Vector3dVector(calcium_left)
    try:
        o3d.io.write_point_cloud(
            str(cv_results_path / "calcium_left.ply"), calcium_left_pcd)
    except:
        print("There is no calium on the left cusp")

    calcium_none_pcd = o3d.geometry.PointCloud()
    calcium_none_pcd.points = o3d.utility.Vector3dVector(calcium_none)
    try:
        o3d.io.write_point_cloud(
            str(cv_results_path / "calcium_none.ply"), calcium_none_pcd)
    except:
        print("There is no calcium on the non-coronary cusp")


def get_stl_volume(stl_file):
    # Load the STL file
    stl_file = mesh.Mesh.from_file(stl_file)
    # Calculate the volume of the mesh
    volume, _, _ = stl_file.get_mass_properties()
    return volume


def get_ply_volume(ply_file):
    """
    Return the volume of a given point cloud file
    """
    # Load the point cloud data
    pcd = o3d.io.read_point_cloud(leaflet_path)
    points = np.asarray(pcd.points)

    # Compute the convex hull of the point cloud
    hull = ConvexHull(points)

    # Calculate the volume of the convex hull
    volume = hull.volume

    return volume