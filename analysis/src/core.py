import sys
import os


this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = os.path.join(this_directory, '..', '..')
sys.path.append(working_dir)


from analysis.src._helpers import calcium_on_cusps_ply, output_dir
from analysis.src._helpers import create_folders
# from analysis.src.geometrical_tools import detect_islands_stl, ply_to_stl

create_folders()

# ply_to_stl(calcium_on_cusps_ply[0], str(output_dir / 'analysis' / "test.stl"), 0.9)

# detect_islands(calcium_on_cusps_ply[1], output_dir/'calcs_corr.stl')

# detect_islands_ply(calcium_on_cusps_ply[0], output_dir/'analysis')


# detect_islands_stl(output_dir/'calcs_corr.stl', output_dir / 'analysis')

def ply_to_stl():

    import pyvista as pv

    # Load PLY file as point cloud
    cloud = pv.read(calcium_on_cusps_ply[0])

    # Perform Poisson surface reconstruction
    surface = cloud.delaunay_3d(alpha=0.0)

    # Convert to triangular mesh
    mesh = surface.extract_geometry().triangulate()

    # mesh = surface.extract_geometry().to_tetrahedra()

    # fill the holes
    mesh = mesh.fill_holes(1000)

    # Save as STL
    mesh.save(str(output_dir / 'analysis'/ 'output.stl'))

# ply_to_stl()

in_file = str(output_dir / 'analysis'/ 'output.stl')
out_file = str(output_dir / 'analysis'/ 'output_fixed.stl')
