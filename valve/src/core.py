import shutil
from pathlib import Path
import os
import sys
import os
import numpy
import vtk
import open3d
import csv
import math
import pymeshlab


from pathlib import Path

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from utils.io import FileFolders
from valve.src import helpers as h
from valve.src import parameters as p


class AVgenerator(object):

    def __init__(self):

        #directory paths
        self.l_letter='L'
        self.nc_letter = 'NC'
        self.r_letter='R'


        self.pointcloud_path = str(FileFolders.folders['valve']['pointcloud'])
        self.shell_path = str(FileFolders.folders['valve']['shell'])
        self.final_path = str(FileFolders.folders['valve']['final'])
        self.aortapath = str(FileFolders.files['cnn']['aorta_stl'])
        self.points_path = str(FileFolders.files['landmark']['landmarks'])

        #parameters
        self.ball_radius = p.ball_radius # radius of ball for ball pivoting meshing algorithm
        self.thickness = p.thickness  # relative thickness of leaflets
        self.topspline_res = p.topspline_res # resolution of the guide spline on the top plane
        self.controlpoint_M = p.curvature_point  # vertical position of centerpoint on the guide curve (LcuspMid,RcuspMid,NCcuspMid
        self.landmark_shift_factor = p.landmark_shift_factor  # shifts landmark points outwards to enable clipping with aorta (lower value means higher shift)
        self.l_controlpoint_C = p.l_controlpoint_C # shifts left coaptation point outwards to create hole in center
        self.nc_controlpoint_C = p.nc_controlpoint_C  # shifts nc coaptation point outwards to create hole in center
        self.r_controlpoint_C = p.r_controlpoint_C  # shifts right coaptation point out to create hole in center

        #landmark points and derived points
        self.p0 = [0, 0, 0]
        self.p1 = [0, 0, 0]
        self.p2 = [0, 0, 0]
        self.p3 = [0, 0, 0]
        self.p4 = [0, 0, 0]
        self.p5 = [0, 0, 0]
        self.p6 = [0, 0, 0]
        self.p4copy = [0.0, 0.0, 0.0] #p4 projected on to closed spline going through p1-p3
        self.p6copy = [0.0, 0.0, 0.0] #p6 projected on to closed spline going through p1-p3
        self.p5copy = [0.0, 0.0, 0.0] #p5 projected on to closed spline going through p1-p3
        self.p0projectedTop = [0.0, 0.0, 0.0] #p0 projected on to plane through p1-p3
        self.p0projected = [0.0, 0.0, 0.0] #p0 projected on to plane through p4-p6
        self.spline_length=0 #stores the number of points on a cross spline -->important for extraction of boundary edges
        self.rcoaptation=[0.0,0.0,0.0]
        self.lcoaptation = [0.0, 0.0, 0.0]
        self.nccoaptation = [0.0, 0.0, 0.0]

    def generateModel(self):
        #this function implements the main_run worklfow of the script:

        # 1. Extract Landmarks
        self.getLandmarks() #gets the landmarks from a csv file

        #2. Project P0 on to bottom and top plane
        self.p0projected = h.ProjectOnPlane(self.p4, self.p5, self.p6, self.p0)
        self.p0projectedTop = h.ProjectOnPlane(self.p1,self.p2, self.p3, self.p0)

        #3. Adjust landmarks to fit to aortic root surface
        self.adjustLandmarks()

        #4. Shift landmarks outwards to intersect with aortic root
        # self.shiftLandmarks()

        #5. Create closed spline throught top and bottom landmarks
        TopCirclePoints = []
        TopCirclePoints.append(self.p1)
        TopCirclePoints.append(self.p2)
        TopCirclePoints.append(self.p3)

        BottomCirclePoints = []
        BottomCirclePoints.append(self.p4)
        BottomCirclePoints.append(self.p5)
        BottomCirclePoints.append(self.p6)

        #convert points into vtk format
        listofPointsBottom_raw=h.vtkSpline(BottomCirclePoints,0.001,1)
        listofPointsBottom=h.array_to_vtk(listofPointsBottom_raw)
        listofPointsTop_raw = h.vtkSpline(TopCirclePoints, 0.001,1)
        listofPointsTop=h.array_to_vtk(listofPointsTop_raw)

        # 6. Create point clouds of cusps
        self.create_cusps(listofPointsTop, listofPointsBottom)

        # 7. Create closed surface shell of cusp. Fuse the individual shells. Clean mesh with meshlab filters
        #left_cusp
        self.closed_surface(self.l_letter,  os.path.join(self.pointcloud_path,'L_pc.ply'),self.lcoaptation)
        self.fuse_shell(self.l_letter)
        # self.meshlab(self.l_letter)
        #nc_cusp
        self.closed_surface(self.nc_letter,  os.path.join(self.pointcloud_path,'NC_pc.ply'),self.nccoaptation)
        self.fuse_shell(self.nc_letter)
        # self.meshlab(self.nc_letter)
        #right_cusp
        self.closed_surface(self.r_letter, os.path.join(self.pointcloud_path,'R_pc.ply'),self.rcoaptation)
        self.fuse_shell(self.r_letter)
        # self.meshlab(self.r_letter)

        #self.bicuspid(listofPointsTop, listofPointsBottom)

    def getLandmarks(self):
        #extracts coordinates of the landmarks from csv file
        pointfile = open(self.points_path)
        csvreader = csv.reader(pointfile, skipinitialspace=True)
        rows = []
        for row in csvreader:
            rows.append(row)

        # self.p4[0]= float(rows[0][0])
        # self.p4[1] = float(rows[0][1])
        # self.p4[2] = float(rows[0][2])

        # self.p6[0]= float(rows[1][0])
        # self.p6[1] = float(rows[1][1])
        # self.p6[2] = float(rows[1][2])

        # self.p5[0] = float(rows[2][0])
        # self.p5[1] = float(rows[2][1])
        # self.p5[2] = float(rows[2][2])

        # self.p1[0] = float(rows[3][0])
        # self.p1[1] = float(rows[3][1])
        # self.p1[2] = float(rows[3][2])

        # self.p3[0] = float(rows[4][0])
        # self.p3[1] = float(rows[4][1])
        # self.p3[2] = float(rows[4][2])

        # self.p2[0] = float(rows[5][0])
        # self.p2[1] = float(rows[5][1])
        # self.p2[2] = float(rows[5][2])

        # self.p0[0] = float(rows[6][0])
        # self.p0[1] = float(rows[6][1])
        # self.p0[2] = float(rows[6][2])
        
        
        
        
        
        self.p4[0]= float(rows[0][0])
        self.p4[1] = float(rows[0][1])
        self.p4[2] = float(rows[0][2])

        self.p6[0]= float(rows[1][0])
        self.p6[1] = float(rows[1][1])
        self.p6[2] = float(rows[1][2])

        self.p5[0] = float(rows[2][0])
        self.p5[1] = float(rows[2][1])
        self.p5[2] = float(rows[2][2])

        self.p1[0] = float(rows[3][0])
        self.p1[1] = float(rows[3][1])
        self.p1[2] = float(rows[3][2])

        self.p3[0] = float(rows[4][0])
        self.p3[1] = float(rows[4][1])
        self.p3[2] = float(rows[4][2])

        self.p2[0] = float(rows[5][0])
        self.p2[1] = float(rows[5][1])
        self.p2[2] = float(rows[5][2])

        self.p0[0] = float(rows[6][0])
        self.p0[1] = float(rows[6][1])
        self.p0[2] = float(rows[6][2]) 

        list = []
        list.append(self.p0)
        list.append(self.p1)
        list.append(self.p2)
        list.append(self.p3)
        list.append(self.p4)
        list.append(self.p5)
        list.append(self.p6)

        vtkPointCloud = h.combinePoints(list,
                                        [])  # combines and converts the list of points to a vtk point cloud

        CuspPolyData = vtk.vtkPolyData()
        CuspPolyData.SetPoints(vtkPointCloud)
        h.PLYExport(CuspPolyData,
                       os.path.join(self.pointcloud_path, 'landmark_test' + '_pc.ply'))

    def create_cusps(self, ListofpointsTop, ListofPointsBottom):
      #this function generates the point clouds resembling the surface of the individual cusps

        #LEFT CUSP

        # Find normal projection of p4 on to the top circle
        self.p4copy = h.findClosestPoint(self.p4, ListofpointsTop, 0)

        # create point on line from p0projection to p4copy. This is used to adjust the convexity of the cusp
        # p.curvature point defines at what relative position between p4copy and p0projected LcuspMid is extracted
        LcuspMid = h.getPointOnLine(self.p4copy, self.p0projected, self.controlpoint_M)

        # Create translation vector point from p0projectedtop outwards to p4 copy
        # This vector is used to shift the center point outwards towards the aortic wall thus creating a small hole between the cusps
        l_outwards = [0.0, 0.0, 0.0]
        l_outwards[0] = self.p4copy[0] - self.p0projectedTop[0]
        l_outwards[1] = self.p4copy[1] - self.p0projectedTop[1]
        l_outwards[2] = self.p4copy[2] - self.p0projectedTop[2]
        l_outwards_mag = h.vectorlength(l_outwards)

        # l_coaptation is control point C for the left cusp.
        # l_controlpoint_C defines how far inwards p0projected top is translated
        l_coaptation = [0.0, 0.0, 0.0]
        l_coaptation[0] = self.p0projectedTop[0] + self.l_controlpoint_C * l_outwards[0] / l_outwards_mag
        l_coaptation[1] = self.p0projectedTop[1] + self.l_controlpoint_C * l_outwards[1] / l_outwards_mag
        l_coaptation[2] = self.p0projectedTop[2] + self.l_controlpoint_C * l_outwards[2] / l_outwards_mag
        self.lcoaptation=l_coaptation

        #this function calculates the optimal position of the control points B.
        relative_distance = self.calculateB(self.p1,self.p2,l_coaptation,0)

        #boundary points B1, B2
        boundary_vector1 = [0.0, 0.0, 0.0]#this vector defines the boundary line from the outer landmark to the projected center
        boundary_vector1[0] = self.p0projectedTop[0] - self.p1[0]
        boundary_vector1[1] = self.p0projectedTop[1] - self.p1[1]
        boundary_vector1[2] = self.p0projectedTop[2] - self.p1[2]
        pointB1 = [0.0, 0.0, 0.0]
        x1 = relative_distance[0]
        pointB1[0] = self.p0projectedTop[0] - x1 * boundary_vector1[0]
        pointB1[1] = self.p0projectedTop[1] - x1 * boundary_vector1[1]
        pointB1[2] = self.p0projectedTop[2] - x1 * boundary_vector1[2]

        boundary_vector2 = [0.0, 0.0, 0.0]
        boundary_vector2[0] = self.p0projectedTop[0] - self.p2[0]
        boundary_vector2[1] = self.p0projectedTop[1] - self.p2[1]
        boundary_vector2[2] = self.p0projectedTop[2] - self.p2[2]
        pointB2 = [0.0, 0.0, 0.0]
        x2 = relative_distance[1]
        pointB2[0] = self.p0projectedTop[0] - x2 * boundary_vector2[0]
        pointB2[1] = self.p0projectedTop[1] - x2 * boundary_vector2[1]
        pointB2[2] = self.p0projectedTop[2] - x2 * boundary_vector2[2]

        #all points on the boundary line from the landmark to the boundary point B1 and B2 are used as input points for the spline
        boundary_points = []
        boundary_points.append(self.p1)
        boundary_points.append(pointB1)
        boundary_line = h.vtkSpline(boundary_points, self.topspline_res, 0)

        #second boundary line.
        boundary_points2 = []
        boundary_points2.append(pointB2)
        boundary_points2.append(self.p2)
        boundary_line2 = h.vtkSpline(boundary_points2, self.topspline_res, 0)

        #create leaflet free edge spline
        free_edge_points = []
        #all points on the boundary line up until the boundary point are fed as input points
        for i in range(0, int(1 * len(boundary_line))):
            free_edge_points.append(boundary_line[i])
        free_edge_points.append(l_coaptation)
        for i in range(int((1 - 1) * len(boundary_line2)), int(len(boundary_line2))):
            free_edge_points.append(boundary_line2[i])

        free_ede_spline_l = h.vtkSpline(free_edge_points, self.topspline_res, 0)

        #create guide spline
        guidesplinelist_l = [] #stores input points of guide spline
        guidesplinelist_l.append(self.p4)
        guidesplinelist_l.append(LcuspMid)
        guidesplinelist_l.append(free_ede_spline_l[int(len(free_ede_spline_l) / 2)])
        guidespline_l = h.vtkSpline(guidesplinelist_l, self.topspline_res * 2, 0)

       #create cross splines between free edge spline and guide spline
        self.cross_splines(free_ede_spline_l, guidespline_l, self.l_letter)


        ################################################################################

        # RIGHT CUSP
        self.p6copy = h.findClosestPoint(self.p6, ListofpointsTop, 0)
        # create point on line from p0projection to p6copy
        RcuspMid = h.getPointOnLine(self.p6copy, self.p0projected, self.controlpoint_M)


        r_outwards = [0.0, 0.0, 0.0]
        r_outwards[0] = self.p6copy[0] - self.p0projectedTop[0]
        r_outwards[1] = self.p6copy[1] - self.p0projectedTop[1]
        r_outwards[2] = self.p6copy[2] - self.p0projectedTop[2]
        r_outwards_mag = h.vectorlength(r_outwards)

        r_coaptation = [0.0, 0.0, 0.0]
        r_coaptation[0] = self.p0projectedTop[0] + self.r_controlpoint_C * r_outwards[0] / r_outwards_mag
        r_coaptation[1] = self.p0projectedTop[1] + self.r_controlpoint_C * r_outwards[1] / r_outwards_mag
        r_coaptation[2] = self.p0projectedTop[2] + self.r_controlpoint_C * r_outwards[2] / r_outwards_mag

        self.rcoaptation=r_coaptation

        relative_distance = self.calculateB(self.p1, self.p3, r_coaptation, 0)

        boundary_vector1 = [0.0, 0.0, 0.0]
        boundary_vector1[0] = self.p0projectedTop[0] - self.p1[0]
        boundary_vector1[1] = self.p0projectedTop[1] - self.p1[1]
        boundary_vector1[2] = self.p0projectedTop[2] - self.p1[2]
        pointB1 = [0.0, 0.0, 0.0]
        x1 = relative_distance[0]
        pointB1[0] = self.p0projectedTop[0] - x1 * boundary_vector1[0]
        pointB1[1] = self.p0projectedTop[1] - x1 * boundary_vector1[1]
        pointB1[2] = self.p0projectedTop[2] - x1 * boundary_vector1[2]

        boundary_vector2 = [0.0, 0.0, 0.0]
        boundary_vector2[0] = self.p0projectedTop[0] - self.p3[0]
        boundary_vector2[1] = self.p0projectedTop[1] - self.p3[1]
        boundary_vector2[2] = self.p0projectedTop[2] - self.p3[2]
        pointB2 = [0.0, 0.0, 0.0]
        x2 = relative_distance[1]
        pointB2[0] = self.p0projectedTop[0] - x2 * boundary_vector2[0]
        pointB2[1] = self.p0projectedTop[1] - x2 * boundary_vector2[1]
        pointB2[2] = self.p0projectedTop[2] - x2 * boundary_vector2[2]

        boundary_points = []
        boundary_points.append(self.p1)
        boundary_points.append(pointB1)
        boundary_line = h.vtkSpline(boundary_points, self.topspline_res, 0)

        # second boundary line.
        boundary_points2 = []
        boundary_points2.append(pointB2)
        boundary_points2.append(self.p3)
        boundary_line2 = h.vtkSpline(boundary_points2, self.topspline_res, 0)

         # defines the relative position on the boundary line where the boundary point is located
        # create leaflet free edge spline
        free_edge_points = []
        # all points on the boundary line up until the boundary point are fed as input points
        for i in range(0, int(1 * len(boundary_line))):
            free_edge_points.append(boundary_line[i])
        free_edge_points.append(r_coaptation)
        for i in range(int((1 - 1) * len(boundary_line2)), int(len(boundary_line2))):
            free_edge_points.append(boundary_line2[i])

        free_edge_spline_r = h.vtkSpline(free_edge_points, self.topspline_res, 0)

        guidesplinelist_r = []
        guidesplinelist_r.append(self.p6)
        guidesplinelist_r.append(RcuspMid)
        guidesplinelist_r.append(free_edge_spline_r[int(len(free_edge_spline_r) / 2)])
        guidespline_r = h.vtkSpline(guidesplinelist_r, self.topspline_res * 2, 0)

        self.cross_splines(free_edge_spline_r, guidespline_r, self.r_letter)


        #############################################################################################
        #NC CUSP

        self.p5copy = h.findClosestPoint(self.p5, ListofpointsTop, 0)
        # create point on line from p0projection to p5copy
        NCcuspMid = h.getPointOnLine(self.p5copy, self.p0projected, self.controlpoint_M)


        # Create translation vector point from p0 projected on to the top point outwards to p5 copy
        # This vector is used to shift the center point outwards towards the aortic wall.
        nc_outwards = [0.0, 0.0, 0.0]
        nc_outwards[0] = self.p5copy[0] - self.p0projectedTop[0]
        nc_outwards[1] = self.p5copy[1] - self.p0projectedTop[1]
        nc_outwards[2] = self.p5copy[2] - self.p0projectedTop[2]
        nc_outwards_mag = h.vectorlength(nc_outwards)

        # nc_point 2 is the turning point of the top spline
        nc_coaptation = [0.0, 0.0, 0.0]
        nc_coaptation[0] = self.p0projectedTop[0] + self.nc_controlpoint_C * nc_outwards[0] / nc_outwards_mag
        nc_coaptation[1] = self.p0projectedTop[1] + self.nc_controlpoint_C * nc_outwards[1] / nc_outwards_mag
        nc_coaptation[2] = self.p0projectedTop[2] + self.nc_controlpoint_C * nc_outwards[2] / nc_outwards_mag
        self.nccoaptation=nc_coaptation
        relative_distance = self.calculateB(self.p2, self.p3, nc_coaptation,1)

        boundary_vector1 = [0.0, 0.0, 0.0]
        boundary_vector1[0] = self.p0projectedTop[0] - self.p2[0]
        boundary_vector1[1] = self.p0projectedTop[1] - self.p2[1]
        boundary_vector1[2] = self.p0projectedTop[2] - self.p2[2]
        pointB1 = [0.0, 0.0, 0.0]
        x1 = relative_distance[0]
        pointB1[0] = self.p0projectedTop[0] - x1 * boundary_vector1[0]
        pointB1[1] = self.p0projectedTop[1] - x1 * boundary_vector1[1]
        pointB1[2] = self.p0projectedTop[2] - x1 * boundary_vector1[2]

        boundary_vector2 = [0.0, 0.0, 0.0]
        boundary_vector2[0] = self.p0projectedTop[0] - self.p3[0]
        boundary_vector2[1] = self.p0projectedTop[1] - self.p3[1]
        boundary_vector2[2] = self.p0projectedTop[2] - self.p3[2]
        pointB2 = [0.0, 0.0, 0.0]
        x2 = relative_distance[1]
        pointB2[0] = self.p0projectedTop[0] - x2 * boundary_vector2[0]
        pointB2[1] = self.p0projectedTop[1] - x2 * boundary_vector2[1]
        pointB2[2] = self.p0projectedTop[2] - x2 * boundary_vector2[2]


        boundary_points = []
        boundary_points.append(self.p2)
        boundary_points.append(pointB1)
        boundary_line = h.vtkSpline(boundary_points, self.topspline_res, 0)

        boundary_points2 = []
        boundary_points2.append(pointB2)
        boundary_points2.append(self.p3)
        boundary_line2 = h.vtkSpline(boundary_points2, self.topspline_res, 0)



        free_edge_points = []
        # all points on the boundary line up until the boundary point are fed as input points
        for i in range(0, int(1 * len(boundary_line))):
            free_edge_points.append(boundary_line[i])
        free_edge_points.append(nc_coaptation)
        for i in range(int((1 - 1) * len(boundary_line2)), int(len(boundary_line2))):
            free_edge_points.append(boundary_line2[i])

        free_edge_spline_nc = h.vtkSpline(free_edge_points, self.topspline_res, 0)


        guidesplinelist_nc = []
        guidesplinelist_nc.append(self.p5)
        guidesplinelist_nc.append(NCcuspMid)
        guidesplinelist_nc.append(free_edge_spline_nc[int(len(free_edge_spline_nc) / 2)])
        guidespline_nc = h.vtkSpline(guidesplinelist_nc, self.topspline_res * 2, 0)

        self.cross_splines(free_edge_spline_nc, guidespline_nc, self.nc_letter)

    def calculateB(self,landmark1,landmark2,coaptation_input,NC):

        #This function is used to calculate the optimal relative position of B1 and B2 on the boundary lines.
        #for this the points on the leaflet free edge curve are rotated and translated to the xy-plane.
        #the free edge curve is shifted so that P0projected is at the origin(0,0,0) and coaptation point C on the y axis
        #The curve is then rotated so that it is symmetric with respect to the y-axis.

        # x-y plane vectors
        origin = [0.0, 0.0, 0.0]
        point1 = [1.0, 0.0, 0.0]
        point2 = [0.0, 1.0, 0.0]

        ##translate points to origin

        p0_origin = h.ProjectOnPlane(origin, point1, point2, self.p0projectedTop)

        translation_vector = [0.0, 0.0, 0.0]
        translation_vector[0] = +origin[0] - p0_origin[0]
        translation_vector[1] = +origin[1] - p0_origin[1]
        translation_vector[2] = +origin[2] - p0_origin[2]

        ##project l_coaptation
        coaptation = h.ProjectOnPlane(origin, point1, point2, coaptation_input)
        coaptation[0] = coaptation[0] + translation_vector[0]
        coaptation[1] = coaptation[1] + translation_vector[1]
        coaptation[2] = coaptation[2] + translation_vector[2]

        # project landmarks on to origin plane
        p1_origin = [0.0, 0.0, 0.0]
        p1_origin = h.ProjectOnPlane(origin, point1, point2, landmark1)
        p1_origin[0] = p1_origin[0] + translation_vector[0]
        p1_origin[1] = p1_origin[1] + translation_vector[1]
        p1_origin[2] = p1_origin[2] + translation_vector[2]

        p2_origin = [0.0, 0.0, 0.0]
        p2_origin = h.ProjectOnPlane(origin, point1, point2, landmark2)
        p2_origin[0] = p2_origin[0] + translation_vector[0]
        p2_origin[1] = p2_origin[1] + translation_vector[1]
        p2_origin[2] = p2_origin[2] + translation_vector[2]


        ## calculate angle between Control Point C-Origin and Unit vector y
        rotation_vector = [0.0, 0.0, 0.0]
        rotation_vector[0] = coaptation[0] - origin[0]
        rotation_vector[1] = coaptation[1] - origin[1]
        rotation_vector[2] = coaptation[2] - origin[2]
        rotation_mag = h.vectorlength(rotation_vector)
        rotation_vector[0] = rotation_vector[0] / rotation_mag
        rotation_vector[1] = rotation_vector[1] / rotation_mag
        rotation_vector[2] = rotation_vector[2] / rotation_mag
        py_unit = [0.0, 1.0, 0.0]
        ScalarDistance = (rotation_vector[0] * py_unit[0]) + (rotation_vector[1] * py_unit[1]) + (
                rotation_vector[2] * py_unit[2])
        angle = -math.acos(ScalarDistance)

        if NC == 1:
            angle = math.acos(ScalarDistance)


        # rotation matrix
        r_m = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        r_m[0][0] = math.cos(angle)
        r_m[0][1] = -math.sin(angle)
        r_m[0][2] = 0
        r_m[1][0] = math.sin(angle)
        r_m[1][1] = math.cos(angle)
        r_m[1][2] = 0
        r_m[2][0] = 0
        r_m[2][1] = 0
        r_m[2][2] = 1


        #rotate coaptation point and landmarks
        coaptation_rotated = [0.0, 0.0, 0.0]
        coaptation_rotated[0] = coaptation[0] * r_m[0][0] + coaptation[1] * r_m[0][1] + coaptation[2] * r_m[0][2]
        coaptation_rotated[1] = coaptation[0] * r_m[1][0] + coaptation[1] * r_m[1][1] + coaptation[2] * r_m[1][2]
        coaptation_rotated[2] = coaptation[0] * r_m[2][0] + coaptation[1] * r_m[2][1] + coaptation[2] * r_m[2][2]

        p1_origin_rotated = [0.0, 0.0, 0.0]
        p1_origin_rotated[0] = p1_origin[0] * r_m[0][0] + p1_origin[1] * r_m[0][1] + p1_origin[2] * r_m[0][2]
        p1_origin_rotated[1] = p1_origin[0] * r_m[1][0] + p1_origin[1] * r_m[1][1] + p1_origin[2] * r_m[1][2]
        p1_origin_rotated[2] = p1_origin[0] * r_m[2][0] + p1_origin[1] * r_m[2][1] + p1_origin[2] * r_m[2][2]

        p2_origin_rotated = [0.0, 0.0, 0.0]
        p2_origin_rotated[0] = p2_origin[0] * r_m[0][0] + p2_origin[1] * r_m[0][1] + p2_origin[2] * r_m[0][2]
        p2_origin_rotated[1] = p2_origin[0] * r_m[1][0] + p2_origin[1] * r_m[1][1] + p2_origin[2] * r_m[1][2]
        p2_origin_rotated[2] = p2_origin[0] * r_m[2][0] + p2_origin[1] * r_m[2][1] + p2_origin[2] * r_m[2][2]

        # calculate angle so that free edge curve is symmetric to y axis
        angle1 = math.atan(p1_origin_rotated[1] / p1_origin_rotated[0]) * 180 / math.pi
        angle2 = math.atan(-p2_origin_rotated[1] / p2_origin_rotated[0]) * 180 / math.pi
        if NC == 1:
            angle2 = math.atan(-p2_origin_rotated[1] / p2_origin_rotated[0]) * 180 / math.pi
        rotation_angle2 = -((angle1 + angle2) / 2 - angle2) * math.pi / 180

        # rotation matrix 2

        r_m2 = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        r_m2[0][0] = math.cos(rotation_angle2)
        r_m2[0][1] = -math.sin(rotation_angle2)
        r_m2[0][2] = 0
        r_m2[1][0] = math.sin(rotation_angle2)
        r_m2[1][1] = math.cos(rotation_angle2)
        r_m2[1][2] = 0
        r_m2[2][0] = 0
        r_m2[2][1] = 0
        r_m2[2][2] = 1


        ##rotate coaption point
        cr1 = coaptation_rotated
        cr2 = [0.0, 0.0, 0.0]
        cr2[0] = cr1[0] * r_m2[0][0] + cr1[1] * r_m2[0][1] + cr1[2] * r_m2[0][2]
        cr2[1] = cr1[0] * r_m2[1][0] + cr1[1] * r_m2[1][1] + cr1[2] * r_m2[1][2]
        cr2[2] = cr1[0] * r_m2[2][0] + cr1[1] * r_m2[2][1] + cr1[2] * r_m2[2][2]

        #translation vector so that coaptation point is algined with y axis again
        translation_vector2 = [0.0, 0.0, 0.0]
        translation_vector2[0] = coaptation_rotated[0] - cr2[0]
        translation_vector2[1] = coaptation_rotated[1] - cr2[1]
        translation_vector2[2] = coaptation_rotated[2] - cr2[2]

        #translate coaptation point
        cr2_translated = [0.0, 0.0, 0.0]
        cr2_translated[0] = cr2[0] + translation_vector2[0]
        cr2_translated[1] = cr2[1] + translation_vector2[1]
        cr2_translated[2] = cr2[2] + translation_vector2[2]

        #rotate and translate landmarks
        sB1 = p1_origin_rotated
        new_sB1 = [0.0, 0.0, 0.0]
        new_sB1[0] = sB1[0] * r_m2[0][0] + sB1[1] * r_m2[0][1] + sB1[2] * r_m2[0][2]
        new_sB1[1] = sB1[0] * r_m2[1][0] + sB1[1] * r_m2[1][1] + sB1[2] * r_m2[1][2]
        new_sB1[2] = sB1[0] * r_m2[2][0] + sB1[1] * r_m2[2][1] + sB1[2] * r_m2[2][2]
        new_sB1[0] = new_sB1[0] + translation_vector2[0]
        new_sB1[1] = new_sB1[1] + translation_vector2[1]
        new_sB1[2] = new_sB1[2] + translation_vector2[2]

        sB2 = p2_origin_rotated
        new_sB2 = [0.0, 0.0, 0.0]
        new_sB2[0] = sB2[0] * r_m2[0][0] + sB2[1] * r_m2[0][1] + sB2[2] * r_m2[0][2]
        new_sB2[1] = sB2[0] * r_m2[1][0] + sB2[1] * r_m2[1][1] + sB2[2] * r_m2[1][2]
        new_sB2[2] = sB2[0] * r_m2[2][0] + sB2[1] * r_m2[2][1] + sB2[2] * r_m2[2][2]
        new_sB2[0] = new_sB2[0] + translation_vector2[0]
        new_sB2[1] = new_sB2[1] + translation_vector2[1]
        new_sB2[2] = new_sB2[2] + translation_vector2[2]


        #calculate relative position of B1 and B2 by approximating spline to be a 2nd order polynomial symmetric to y-axis

        positionvector=[]

        #PositionB1
        delta_y1 = new_sB1[1] - origin[1]
        delta_x1 = new_sB1[0] - origin[0]
        slope = delta_y1 / delta_x1
        c = cr2_translated[1]
        coef_a = (slope * slope) / (4 * c)

        Bx = 2 * c / slope
        By = Bx * slope
        pointB = [Bx, By, 0.0]


        ##find relative position of B on curve

        point_B = [Bx, By, 0]
        len_B = h.vectorlength(point_B)
        total_len = h.vectorlength(new_sB1)

        relative_length = len_B / total_len
        positionvector.append(relative_length)

        # PositionB2
        delta_y1 = new_sB2[1] - origin[1]
        delta_x1 = new_sB2[0] - origin[0]
        slope = delta_y1 / delta_x1
        c = cr2_translated[1]
        coef_a = (slope * slope) / (4 * c)
        Bx = 2 * c / slope
        By = Bx * slope
        pointB = [Bx, By, 0.0]

        ##find relative position of B on curve

        point_B = [Bx, By, 0]
        len_B = h.vectorlength(point_B)
        total_len = h.vectorlength(new_sB2)

        relative_length = len_B / total_len
        positionvector.append(relative_length)
        print('position_vector: ',positionvector)

        return positionvector

    def cross_splines(self, topspline, midspline, cusp_letter):
        surfacepoints = []
        total = len(topspline)

        for i in range(0, len(midspline) - 1, 1):
            splinepoints = []
            splinepoints.append(topspline[i])
            splinepoints.append(midspline[i])
            splinepoints.append(topspline[total - i - 1])
            pointsA = h.vtkSpline(splinepoints, p.crossspline_res, 0)
            self.spline_length = len(pointsA)
            surfacepoints.append(pointsA)

        # adds the control point C (or midpoint of the guide spline) to the point cloud
        list = []
        list.append(midspline[len(midspline) - 1])

        vtkPointCloud = h.combinePoints(list,
                                        surfacepoints)  # combines and converts the list of points to a vtk point cloud

        CuspPolyData = vtk.vtkPolyData()
        CuspPolyData.SetPoints(vtkPointCloud)
        h.PLYExport(CuspPolyData,
                       os.path.join(self.pointcloud_path, cusp_letter + '_pc.ply'))


    def closed_surface(self, letter, path,cusp):
        x=1 #important for direction of offset.
        # read pointcloud
        cloud = h.readPointCloud(path)
        self.surface_mesh(cloud, self.ball_radius, os.path.join(self.shell_path, letter + '_shell.ply'))
        #open3d.visualization.draw_geometries([cloud],point_show_normal=True)

        #This step ensures that the point clout is offset in the correct direction
        numpycloud=numpy.asarray(cloud.points)
        vtkcloud=h.array_to_vtk(numpycloud)
        coaptation=h.findClosestPoint(cusp,vtkcloud,0)
        result=numpy.where(numpycloud == coaptation)

        normal_coap=cloud.normals[result[0][0]]
        direction=[0.0,0.0,0.0]
        direction[0]=cusp[0]-self.p0projectedTop[0]
        direction[1] = cusp[1] - self.p0projectedTop[1]
        direction[2] = cusp[2] - self.p0projectedTop[2]
        ScalarDistance = (direction[0] * normal_coap[0]) + (direction[1] * normal_coap[1]) + (
                direction[2] * normal_coap[2])

        if ScalarDistance >0 :
            x=1
        else:
            x=-1

        ## create offset surface pointcloud and shell
        offset_cloud = self.createOffset(cloud, x)
        offset_cloud.estimate_normals()
        offset_cloud.normalize_normals()
        offset_cloud.orient_normals_consistent_tangent_plane(6)
        open3d.io.write_point_cloud(os.path.join(self.pointcloud_path, letter + '_offset_pc.ply'), offset_cloud)
        self.surface_mesh(offset_cloud, self.ball_radius, os.path.join(self.shell_path, letter + '_offset_shell.ply'))

        # create thickness
        solid_cloud = self.createThickness(cloud, x)
        open3d.io.write_point_cloud(os.path.join(self.pointcloud_path, letter + '_solid_pc.ply'), solid_cloud)
        #open3d.visualization.draw_geometries([solid_cloud])

        # extract boundaries
        np_boundary = numpy.asarray(solid_cloud.points)
        boundary_length = len(np_boundary)
        index=int(boundary_length/2)-1
        boundary_top = []
        boundary_side = []

        for i in range(0, self.spline_length):
            storage = np_boundary[i, :]
            boundary_top.append(storage)
        for i in range(int(boundary_length / 2), int(boundary_length / 2) + self.spline_length):
            storage = np_boundary[i, :]
            boundary_top.append(storage)


        for i in range(0, int(boundary_length/2), self.spline_length):
            storage1 = np_boundary[i, :]
            boundary_side.append(storage1)
        for i in range(1, int(boundary_length/2), self.spline_length):
            storage1 = np_boundary[i, :]
            boundary_side.append(storage1)
        for i in range(int(boundary_length / 2)+1, boundary_length, self.spline_length):
            storage1 = np_boundary[i, :]
            boundary_side.append(storage1)
        for i in range(int(boundary_length/2),boundary_length,self.spline_length):
            storage1 = np_boundary[i, :]
            boundary_side.append(storage1)

        ##find coaptation point

        vtkboundary=h.array_to_vtk(boundary_side)
        centerpoint=h.findClosestPoint(self.rcoaptation,vtkboundary,0)


        #mesh surface of boundary
        boundarytop = open3d.geometry.PointCloud()
        boundarytop.points = open3d.utility.Vector3dVector(boundary_top)
        boundarytop.estimate_normals()
        boundarytop.normalize_normals()
        boundarytop.orient_normals_consistent_tangent_plane(2)
        open3d.io.write_point_cloud(
            os.path.join(self.pointcloud_path, letter + '_boundary1_pc.ply'), boundarytop)
        self.surface_mesh(boundarytop, self.ball_radius,
                          os.path.join(self.shell_path, letter + '_boundary1_shell.ply'))

        boundary = open3d.geometry.PointCloud()
        boundary.points = open3d.utility.Vector3dVector(boundary_side)
        boundary.estimate_normals()
        boundary.normalize_normals()
        boundary.orient_normals_consistent_tangent_plane(2)
        open3d.io.write_point_cloud(
            os.path.join(self.pointcloud_path, letter + '_boundary2_pc.ply'),
            boundary)
        self.surface_mesh(boundary, self.ball_radius, os.path.join(self.shell_path, letter + '_boundary2_shell.ply'))


    def fuse_shell(self, letter):
        #this functions reads the individual surface meshes and combines them to one
        shell = h.readPLY(os.path.join(self.shell_path, letter + '_shell.ply'))
        offset_shell = h.readPLY(os.path.join(self.shell_path, letter + '_offset_shell.ply'))
        boundary1 = h.readPLY(os.path.join(self.shell_path, letter + '_boundary1_shell.ply'))
        boundary2 = h.readPLY(os.path.join(self.shell_path, letter + '_boundary2_shell.ply'))
        combined = h.appendData(shell, offset_shell, boundary1, boundary2)
        h.PLYExport(combined, os.path.join(self.shell_path, letter + '_complete_cusp.ply'))

    def surface_mesh(self, cloud, factor, path):
        # implementation of ball pivoting algorithm using open3d
        distances = cloud.compute_nearest_neighbor_distance()
        avg_dist = numpy.mean(distances)
        ball_radius = factor * avg_dist
        bpa_mesh = open3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(cloud,
                                                                                      open3d.utility.DoubleVector(
                                                                                          [ball_radius]))

        open3d.io.write_triangle_mesh(path, bpa_mesh)

    def createOffset(self, cloud, x):
        #this function converts every point in the open3d point cloud into a numpy array
        thickness = self.thickness
        np_cloud_original = numpy.asarray(cloud.points)
        cloud_len = len(np_cloud_original)
        np_cloud_copy = []
        #the normals of every point are added to the individual point in the point cloud
        for i in range(0, cloud_len):
            storage = numpy.add(np_cloud_original[i], x * thickness * cloud.normals[i])
            np_cloud_copy.append(storage)

        #the offset point cloud is converted back into a open3d point cloud and returned
        cloud_test = open3d.geometry.PointCloud()
        cloud_test.points = open3d.utility.Vector3dVector(np_cloud_copy)

        return cloud_test

    def createThickness(self, cloud, x):
        #same procedure as the create offset function with the difference that the offset point cloud is fused with the original point cloud before returning
        thickness = self.thickness
        np_cloud_original = numpy.asarray(cloud.points)
        cloud_len = len(np_cloud_original)
        np_cloud_copy = []

        for i in range(0, cloud_len):
            storage = numpy.add(np_cloud_original[i], x * thickness * cloud.normals[i])
            np_cloud_copy.append(storage)

        cloud_test = open3d.geometry.PointCloud()
        cloud_test.points = open3d.utility.Vector3dVector(np_cloud_copy)
        combined_points = open3d.geometry.PointCloud()
        combined_points += cloud
        combined_points += cloud_test

        return combined_points

    def shiftLandmarks(self):
        # shift landmarks inwards
        # point 1
        inwards_vector = [0.0, 0.0, 0.0]
        inwards_vector[0] = self.p1[0] - self.p0projectedTop[0]
        inwards_vector[1] = self.p1[1] - self.p0projectedTop[1]
        inwards_vector[2] = self.p1[2] - self.p0projectedTop[2]
        magnitude = h.vectorlength(inwards_vector) * self.landmark_shift_factor
        shifted = [0.0, 0.0, 0.0]
        shifted[0] = self.p1[0] + inwards_vector[0] / magnitude
        shifted[1] = self.p1[1] + inwards_vector[1] / magnitude
        shifted[2] = self.p1[2] + inwards_vector[2] / magnitude
        self.p1 = shifted

        inwards_vector2 = [0.0, 0.0, 0.0]
        inwards_vector2[0] = self.p2[0] - self.p0projectedTop[0]
        inwards_vector2[1] = self.p2[1] - self.p0projectedTop[1]
        inwards_vector2[2] = self.p2[2] - self.p0projectedTop[2]
        magnitude2 = h.vectorlength(inwards_vector2) * self.landmark_shift_factor
        shifted2 = [0.0, 0.0, 0.0]
        shifted2[0] = self.p2[0] + inwards_vector2[0] / magnitude2
        shifted2[1] = self.p2[1] + inwards_vector2[1] / magnitude2
        shifted2[2] = self.p2[2] + inwards_vector2[2] / magnitude2
        self.p2 = shifted2

        inwards_vector3 = [0.0, 0.0, 0.0]
        inwards_vector3[0] = self.p3[0] - self.p0projectedTop[0]
        inwards_vector3[1] = self.p3[1] - self.p0projectedTop[1]
        inwards_vector3[2] = self.p3[2] - self.p0projectedTop[2]
        magnitude3 = h.vectorlength(inwards_vector3) * self.landmark_shift_factor
        shifted3 = [0.0, 0.0, 0.0]
        shifted3[0] = self.p3[0] + inwards_vector3[0] / magnitude3
        shifted3[1] = self.p3[1] + inwards_vector3[1] / magnitude3
        shifted3[2] = self.p3[2] + inwards_vector3[2] / magnitude3
        self.p3 = shifted3

        inwards_vector4 = [0.0, 0.0, 0.0]
        inwards_vector4[0] = self.p4[0] - self.p0projectedTop[0]
        inwards_vector4[1] = self.p4[1] - self.p0projectedTop[1]
        inwards_vector4[2] = self.p4[2] - self.p0projectedTop[2]
        magnitude4 = h.vectorlength(inwards_vector4) * self.landmark_shift_factor
        shifted4 = [0.0, 0.0, 0.0]
        shifted4[0] = self.p4[0] + inwards_vector4[0] / magnitude4
        shifted4[1] = self.p4[1] + inwards_vector4[1] / magnitude4
        shifted4[2] = self.p4[2] + inwards_vector4[2] / magnitude4
        self.p4 = shifted4

        inwards_vector5 = [0.0, 0.0, 0.0]
        inwards_vector5[0] = self.p5[0] - self.p0projectedTop[0]
        inwards_vector5[1] = self.p5[1] - self.p0projectedTop[1]
        inwards_vector5[2] = self.p5[2] - self.p0projectedTop[2]
        magnitude5 = h.vectorlength(inwards_vector5) * self.landmark_shift_factor
        shifted5 = [0.0, 0.0, 0.0]
        shifted5[0] = self.p5[0] + inwards_vector5[0] / magnitude5
        shifted5[1] = self.p5[1] + inwards_vector5[1] / magnitude5
        shifted5[2] = self.p5[2] + inwards_vector5[2] / magnitude5
        self.p5 = shifted5

        inwards_vector6 = [0.0, 0.0, 0.0]
        inwards_vector6[0] = self.p6[0] - self.p0projectedTop[0]
        inwards_vector6[1] = self.p6[1] - self.p0projectedTop[1]
        inwards_vector6[2] = self.p6[2] - self.p0projectedTop[2]
        magnitude6 = h.vectorlength(inwards_vector6) * self.landmark_shift_factor
        shifted6 = [0.0, 0.0, 0.0]
        shifted6[0] = self.p6[0] + inwards_vector6[0] / magnitude6
        shifted6[1] = self.p6[1] + inwards_vector6[1] / magnitude6
        shifted6[2] = self.p6[2] + inwards_vector6[2] / magnitude6
        self.p6 = shifted6

    def adjustLandmarks(self):

        aorta_data = h.readSTL(self.aortapath)
        aorta_points = vtk.vtkPoints()
        aorta_points = aorta_data.GetPoints()
        new_p1 = h.findClosestPoint(self.p1, aorta_points, 0)
        new_p2 = h.findClosestPoint(self.p2, aorta_points, 0)
        new_p3 = h.findClosestPoint(self.p3, aorta_points, 0)
        new_p4 = h.findClosestPoint(self.p4, aorta_points, 0)
        new_p5 = h.findClosestPoint(self.p5, aorta_points, 0)
        new_p6 = h.findClosestPoint(self.p6, aorta_points, 0)

        self.p1 = new_p1
        self.p2 = new_p2
        self.p3 = new_p3
        self.p4 = new_p4
        self.p5 = new_p5
        self.p6 = new_p6

    def meshlab(self,letter):
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(os.path.join(self.shell_path, letter + '_complete_cusp.ply'))
        ms.close_holes(maxholesize=200)
        ms.merge_close_vertices()
        ms.save_current_mesh(os.path.join(self.final_path, letter + '_meshlab_cusp.ply'))
