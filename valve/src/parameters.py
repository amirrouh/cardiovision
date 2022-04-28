from pathlib import Path
import os

# file and folders
this_directory = os.path.abspath(os.path.dirname(__file__))
project_path = Path(os.path.join(this_directory, '..'))

#parameters
ball_radius=3.2 #radius of ball for ball pivoting meshing algorithm
thickness=0.2 #thickness of leaflets
topspline_res=0.005 #resolution of the guide spline on the top plane
crossspline_res=0.0095
curvature_point=0.7 #vertical position of centerpoint on the guide curve (LcuspMid,RcuspMid,NCcuspMid
landmark_shift_factor=0.53 #shifts landmark points outwards to enable clipping with aorta

#Cusp Design Parameters

l_controlpoint_C=1.9 #shifts left coaptation point outwards
nc_controlpoint_C=0.8 #shifts nc coaptation point outwards
r_controlpoint_C=1.9 #shifts right coaptation point out
