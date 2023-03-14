import sys
import os
import shutil
from pathlib import Path
import numpy as np
import open3d as o3d
import pandas as pd


this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = os.path.join(this_directory, '..', '..')
sys.path.append(working_dir)

from config import output_dir



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
