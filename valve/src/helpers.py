import numpy
import vtk
import math
import open3d

def getPointOnLine(point1, point2, factor):
    # gets point on a line between two points with factor being the relative distance inbetween the two

    vector = [0.0, 0.0, 0.0]
    vector[0] = point2[0] - point1[0]
    vector[1] = point2[1] - point1[1]
    vector[2] = point2[2] - point1[2]
    PointOnLine = [0.0, 0.0, 0.0]
    PointOnLine[0] = point1[0] + factor * vector[0]
    PointOnLine[1] = point1[1] + factor * vector[1]
    PointOnLine[2] = point1[2] + factor * vector[2]
    return PointOnLine

def ProjectOnPlane(point1, point2, point3, target):
    # projects target point on to plane defined by point1-point3

    ##Calculate plane Normal
    vector1 = [0.0, 0.0, 0.0]
    vector2 = [0.0, 0.0, 0.0]

    vector1[0] = point2[0] - point1[0]
    vector1[1] = point2[1] - point1[1]
    vector1[2] = point2[2] - point1[2]

    vector2[0] = point3[0] - point1[0]
    vector2[1] = point3[1] - point1[1]
    vector2[2] = point3[2] - point1[2]

    normal = numpy.cross(vector1, vector2)

    # normalize normal
    x = (normal[0] * normal[0]) + (normal[1] * normal[1]) + (normal[2] * normal[2])
    magnitude = numpy.sqrt(x)
    normal[0] = normal[0] / magnitude
    normal[1] = normal[1] / magnitude
    normal[2] = normal[2] / magnitude

    ##Calculate distance vector between target point and point1 on plane
    distanceVector = [0.0, 0.0, 0.0]
    distanceVector[0] = target[0] - point1[0]
    distanceVector[1] = target[1] - point1[1]
    distanceVector[2] = target[2] - point1[2]

    # Calculate scalar normal distance of target point to p1
    ScalarDistance = (distanceVector[0] * normal[0]) + (distanceVector[1] * normal[1]) + (
            distanceVector[2] * normal[2])

    # Add scaled normal vector to target point to create projected point
    projectedPoint = [0.0, 0.0, 0.0]
    projectedPoint[0] = target[0] - ScalarDistance * normal[0]
    projectedPoint[1] = target[1] - ScalarDistance * normal[1]
    projectedPoint[2] = target[2] - ScalarDistance * normal[2]

    return projectedPoint

def findClosestPoint(targetPoint, listofPoints, x):
    # finds closest point of a target point within a list of points in vtk format
    # x is equal to 1 if the target point is in the listofPoints is self, otherwise it is zero
    distancearray = []
    listofcoordinates = []
    nOfPoints = listofPoints.GetNumberOfPoints()

    # extracts all points from the vtk point class list and stores them in a regular array
    # calculates distance between target point and every point in the list and stores in distance array
    for i in range(0, nOfPoints):
        coord = [0.0, 0.0, 0.0]
        listofPoints.GetPoint(i, coord)
        listofcoordinates.append(coord)
        squaredDistance = (
                (coord[0] - targetPoint[0]) * (coord[0] - targetPoint[0]) + (coord[1] - targetPoint[1]) * (
                coord[1] - targetPoint[1]) + (coord[2] - targetPoint[2]) * (coord[2] - targetPoint[2]))
        distance = numpy.sqrt(squaredDistance)
        distancearray.append(distance)

    # finds the position of the element with the smallest distance
    minDistance = min(distancearray)
    index = distancearray.index(minDistance)

    # the closest point is therefore the point in the original list at that index position
    nearestPoint = [listofcoordinates[index + x]]

    return nearestPoint[0]

def combinePoints(single_spline, spline_mesh):
    # combines a list of points and returns it as a vtkPoints class
    # single_spline is a list of points on the spline
    # spline_mesh is a list of splines, each containing a list of points

    list = []
    list = single_spline
    length1 = len(spline_mesh)
    for i in range(0, length1):
        list = list + spline_mesh[i]

    points = vtk.vtkPoints()

    pid = [0] * len(list)
    length = len(list)

    for i in range(0, length):
        pid[i] = points.InsertNextPoint(list[i])

    return points

def Intervals(step):
    # defines intervals where points on splines are evaluated
    x = 0
    intervals = []
    while x < 1:
        intervals.append(x)
        x = x + step
    intervals.append(1)

    return intervals

def vtkSpline(list, resolution, closed):
    # creates a vtk spline from a list of points and returns a list of points on the spline.
    # both input and output are not in vtk format
    colors = vtk.vtkNamedColors()
    spline = vtk.vtkParametricSpline()

    if closed == 1:
        spline.ClosedOn()
    points = vtk.vtkPoints()
    length = len(list)
    points = vtk.vtkPoints()
    for i in range(0, length):
        points.InsertNextPoint(list[i])
    spline.SetPoints(points)

    # extract points on spline
    Du = [0.0] * 9

    listOfPoints = []
    Range = Intervals(resolution)

    for x in Range:
        U = [x, x, x]
        Location = [0.0, 0.0, 0.0]
        spline.Evaluate(U, Location, Du)
        listOfPoints.append(Location)
    return listOfPoints

def appendData(pd1, pd2, pd3, pd4):

    app = vtk.vtkAppendPolyData()
    app.AddInputData(pd1)
    app.AddInputData(pd2)
    app.AddInputData(pd3)
    app.AddInputData(pd4)
    app.Update()
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(app.GetOutput())
    cleaner.Update()

    result = cleaner.GetOutput()

    return result

def vectorlength(vector):
    length = vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2]
    x=math.sqrt(length)
    return x

def array_to_vtk(list):
    #inserts a list of points into a vtk point cloud entity
    points = vtk.vtkPoints()

    pid = [0] * len(list)
    length = len(list)

    for i in range(0, length):
        pid[i] = points.InsertNextPoint(list[i])

    return points

def PLYExport(polydata, path):
    # exports a polydata set to a vtk file
    writer = vtk.vtkPLYWriter()
    writer.SetInputData(polydata)
    writer.SetFileName(path)
    writer.Write()

def readSTL(path):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(path)
    reader.Update()
    polydata = reader.GetOutput()
    return polydata

def STLExport(self, polydata, path):
    stlWriter = vtk.vtkSTLWriter()
    stlWriter.SetFileName(path)
    stlWriter.SetInputData(polydata)
    stlWriter.Write()

def readPLY(path):
    reader = vtk.vtkPLYReader()
    reader.SetFileName(path)
    reader.Update()
    polydata = reader.GetOutput()
    return polydata

def readPointCloud(path):
    #reads a point cloud into a open3d point cloud entity
    cloud = open3d.io.read_point_cloud(path)# Read the point cloud

    cloud.estimate_normals()
    cloud.normalize_normals()
    cloud.orient_normals_consistent_tangent_plane(3)

    return cloud
