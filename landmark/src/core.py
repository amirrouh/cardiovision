import os.path
import sys


import SimpleITK as sitk
import cv2
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.signal import argrelextrema

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from landmark.src.helpers import Math, Image
from utils.io import FileFolders, Functions

files = FileFolders.files['landmark']


class DetectLandmarks:
    def __init__(self, aorta_nrrd_file):
        self.aorta_nrrd_file = aorta_nrrd_file
        self.sitk_img = sitk.ReadImage(self.aorta_nrrd_file)
        self.arr_sitk = sitk.GetArrayFromImage(self.sitk_img)
        self.arr = []
        for img in self.arr_sitk:
            if np.count_nonzero(img) > 10:
                self.arr.append(Image.keep_largest(img))
            
        self.sitk_img.SetOrigin((0, 0, 0))
        self.sitk_img.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))

    def get_metadata(self):
        if not os.path.isfile(files['image_data']):
            nx, ny, slide_num = self.sitk_img.GetSize()
            dx, dy, dz = self.sitk_img.GetSpacing()
            results = {
                'nx': nx,
                'ny': ny,
                'slide_num': slide_num,
                'dx': dx,
                'dy': dy,
                'dz': dz,
            }
            Functions.save_pickle(results, files['image_data'])
        else:
            results = Functions.read_pickle(files['image_data'])
        return results

    def drawings(self):
        if not os.path.isfile(files['drawings']):           
            circles, circle_similarity = Image.draw_circles(np.copy(self.arr))
            triangles, triangle_similarity, equilateral_ratio, triangle_centroids, midpoints, edges, coords_of_min_angle_vertex = \
                Image.draw_triangles(
                    np.copy(self.arr))
            ellipses, ellipses_params, eccentricity_list, angle_list = Image.draw_ellipses(np.copy(self.arr))
            aorta_areas = Image.aorta_cross_section_area(np.copy(self.arr))

            results = {
                # circle params
                'circles': circles,
                'circle_similarity': circle_similarity,
                # triangle params
                'triangles': triangles,
                'triangle_similarity': triangle_similarity,
                'equilateral_ratio': equilateral_ratio,
                'triangle_centroids': triangle_centroids,
                'midpoints': midpoints,
                'edges': edges,
                'coords_of_min_angle_vertex': coords_of_min_angle_vertex,
                # ellipse params
                'ellipses': ellipses,
                'ellipses_params': ellipses_params,
                'eccentricity_list': eccentricity_list,
                'angle_list': angle_list,
                # aorta params
                'aorta_areas': aorta_areas
            }

            Functions.save_pickle(results, files['drawings'])
        else:
            results = Functions.read_pickle(files['drawings'])
        return results

    def get_indices(self):
        """
        Returns coronaries slide number, top plane slide number and bottom plane slide number
        """
        drawings = self.drawings()

        circle_similarity = drawings['circle_similarity']
        triangle_similarity = drawings['triangle_similarity']
        aorta_areas = drawings['aorta_areas']
        
        n_slides = len(aorta_areas)
        
        circle_similarity_reverse = circle_similarity
        circle_similarity_reverse.reverse()
        
        triangle_similarity_reverse = triangle_similarity
        triangle_similarity_reverse.reverse()
        

        if not os.path.isfile(files['indices']):
            
            coronaries_candidates = argrelextrema(np.array(circle_similarity_reverse), np.less, order=2)[0]
            for i in coronaries_candidates:
                if circle_similarity_reverse[i] < triangle_similarity_reverse[i]:
                    coronaries_idx = n_slides - i
          
            _aorta_areas = aorta_areas.copy()
            _aorta_areas.reverse()
            _slope = Math.calc_avg_slope(_aorta_areas, 10)
            top_idx = n_slides - np.argmax(_slope)
            bottom_idx = n_slides - np.argmin(_slope)

            results = {
                'coronaries_idx': coronaries_idx,
                'top_idx': top_idx,
                'bottom_idx': bottom_idx,
            }

            Functions.save_pickle(results, files['indices'])
        else:
            results = Functions.read_pickle(files['indices'])
        return results

    def get_triangles(self):
        """
        calc triangle information on top and bottom planes including:

        centroid, midpoints, edges, euler_lines (connecting centroid to vertices), angles (euler lines to horizontal)
        """
        drawings = self.drawings()
        indices = self.get_indices()

        if not os.path.isfile(files['triangles_info']):
            top_idx = indices['top_idx']
            bottom_idx = indices['bottom_idx']

            centroids = drawings['triangle_centroids']
            midpoints = drawings['midpoints']
            edges = drawings['edges']
            coords_of_min_angle_vertex = drawings['coords_of_min_angle_vertex']

            centroid_top = centroids[top_idx]
            centroid_bottom = centroids[bottom_idx]
            midpoints_top = midpoints[top_idx]
            midpoints_bottom = midpoints[bottom_idx]
            edges_top = edges[top_idx]
            edges_bottom = edges[bottom_idx]

            bottom_euler_lines = []
            for i in range(3):
                l = Math.line_from_points(centroid_bottom, edges_bottom[i])
                bottom_euler_lines.append(l)

            top_euler_lines = []
            for i in range(3):
                l = Math.line_from_points(centroid_top, midpoints_top[i])
                top_euler_lines.append(l)

            bottom_angles = []
            for b in bottom_euler_lines:
                m = b[0]  # slope
                angel = np.rad2deg(np.arctan(m))
                if angel >= 0:
                    bottom_angles.append(angel)
                else:
                    bottom_angles.append(angel)

            top_angles = []
            for b in top_euler_lines:
                m = b[0]  # slope
                angel = np.rad2deg(np.arctan(m))
                if angel >= 0:
                    top_angles.append(angel)
                else:
                    top_angles.append(angel + 360)

            results = {
                'centroid_top': centroid_top,
                'centroid_bottom': centroid_bottom,
                'midpoints_top': midpoints_top,
                'midpoints_bottom': midpoints_bottom,
                'edges_top': edges_top,
                'edges_bottom': edges_bottom,
                'bottom_euler_lines': bottom_euler_lines,
                'top_euler_lines': top_euler_lines,
                'bottom_angles': bottom_angles,
                'top_angles': top_angles,
                'coords_of_min_angle_vertex': coords_of_min_angle_vertex
            }

            Functions.save_pickle(results, files['triangles_info'])
        else:
            results = Functions.read_pickle(files['triangles_info'])
        return results

    def get_bottom_landmarks(self):
        """
        Returns the bottom landmarks and the landmark coordinate where the triangle angel is minimum
         (close to left coronary)
        """
        indices = self.get_indices()
        bottom_idx = indices['bottom_idx']
        triangles_info = self.get_triangles()
        centroid_bottom = triangles_info['centroid_bottom']
        edges_bottom = triangles_info['edges_bottom']
        img = np.copy(self.arr[bottom_idx])
        nx, ny = img.shape
        x_c, y_c = centroid_bottom
        landmark_angle_list_bottom = []
        _landmark_lines = []
        bottom_landmark_coords = []
        for edge in edges_bottom:
            _landmark_line = []
            e = np.array(edge)
            c = np.array(centroid_bottom)
            x_axis = np.array([1, 0])
            ce = e - c
            angle = np.arctan2(ce[1], ce[0]) - np.arctan2(x_axis[1], x_axis[0])
            landmark_angle_list_bottom.append(angle)
            r = 0
            dr = 1
            (x, y) = centroid_bottom

            while (0 <= x < nx) and (0 <= y < ny):
                x = int(r * np.cos(angle) + x_c)
                y = int(r * np.sin(angle) + y_c)
                try:
                    _landmark_line.append((x, y, img[y, x]))
                    r += dr
                except:
                    break

            _landmark_lines.append(_landmark_line)
            _landmark_line_nonzero = []
            for i in _landmark_line:
                if i[2] != 0:
                    _landmark_line_nonzero.append(i[:2])
            bottom_landmark_coords.append(_landmark_line_nonzero[-1])

        return bottom_landmark_coords

    def get_top_landmarks(self):
        
        indices = self.get_indices()
        triangles_info = self.get_triangles()
        top_idx = indices['top_idx']
        centroid_top = triangles_info['centroid_top']
        midpoints_bottom = triangles_info['midpoints_bottom']
        midpoints_top = triangles_info['midpoints_top']

        img = np.copy(self.arr[top_idx])
        nx, ny = img.shape
        lines_pixel_values_top = []
        x_c, y_c = centroid_top
        landmark_r_list = []
        landmark_angle_list_top = []
        # for midpoint in midpoints_bottom:
        for midpoint in midpoints_top:
            line_pixel_values = []
            m = np.array(midpoint)
            c = np.array(centroid_top)
            x_axis = np.array([1, 0])
            cm = m - c
            angle = np.arctan2(cm[1], cm[0]) - np.arctan2(x_axis[1], x_axis[0])
            landmark_angle_list_top.append(angle)
            r = 0
            dr = 1
            (x, y) = centroid_top
            while (0 <= x < nx) and (0 <= y < ny):
                x = int(r * np.cos(angle) + x_c)
                y = int(r * np.sin(angle) + y_c)
                try:
                    line_pixel_values.append(img[y, x])
                    r += dr
                except:
                    break
            lines_pixel_values_top.append(Math.pop_zeros(line_pixel_values))
            landmark_r_list.append(dr * len(line_pixel_values))

        top_landmark_coords_list = []
        for i in range(3):
            r = landmark_r_list[i]
            angle = landmark_angle_list_top[i]
            x = int(r * np.cos(angle) + x_c)
            y = int(r * np.sin(angle) + y_c)
            top_landmark_coords_list.append((x, y))
        return top_landmark_coords_list

    def calc_landmark_angles(self):
        """
        Returns: calculates the slope of the lines connecting triangle centroid to the landmarks
        """
        indices = self.get_indices()
        drawings = self.drawings()

        top_idx = indices['top_idx']
        bottom_idx = indices['bottom_idx']
        centroids = drawings['triangle_centroids']
        midpoints = drawings['midpoints']
        edges = drawings['edges']

        centroid_top = centroids[top_idx]
        centroid_bottom = centroids[bottom_idx]
        midpoints_top = midpoints[top_idx]
        edges_bottom = edges[bottom_idx]

        bottom_lines = []
        for i in range(3):
            l = Math.line_from_points(centroid_bottom, edges_bottom[i])
            bottom_lines.append(l)

        top_lines = []
        for i in range(3):
            l = Math.line_from_points(centroid_top, midpoints_top[i])
            top_lines.append(l)

        bottom_angles = []
        for b in bottom_lines:
            m = b[0]  # slope
            angel = np.rad2deg(np.arctan(m))
            if angel >= 0:
                bottom_angles.append(angel)
            else:
                bottom_angles.append(angel + 360)

        top_angles = []
        for b in top_lines:
            m = b[0]  # slope
            angel = np.rad2deg(np.arctan(m))
            if angel >= 0:
                top_angles.append(angel)
            else:
                top_angles.append(angel + 360)

        return bottom_angles, top_angles

    def bottom_landmarks(self):
        """

        Returns: Left, right, and non cuspid landmark coordinates

        """
        indices = self.get_indices()
        drawings = self.drawings()
        ellipses, ellipses_params, eccentricity_list, angle_list = Image.draw_ellipses(np.copy(self.arr))
        coronaries_idx = indices['coronaries_idx']
        bottom_idx = indices['bottom_idx']
        triangle_centroids = drawings['triangle_centroids']
        bottom_centroid = triangle_centroids[bottom_idx]
        bottom_landmark_coords = self.get_bottom_landmarks()
        m = angle_list[coronaries_idx]
        _landmarks = []
        for blm in bottom_landmark_coords:
            _landmarks.append([blm, Math.distance_point_line(blm, m, bottom_centroid)])
        _arr = np.array(_landmarks, dtype='object')
        _arr = _arr[_arr[:, 1].argsort()]
        left_cusp_lm, right_cusp_lm, non_cusp_lm = _arr[:, 0]
        return left_cusp_lm, right_cusp_lm, non_cusp_lm

    def top_landmarks(self):
        """
        P4 is pick of left cusp, P5 is on the non coronary cusp and P6 in on the right cusp\
        2- P1 between left and right; P2 between left and None; P3 between right and None
        Returns:
        """
        left, right, non = self.bottom_landmarks()
        top_landmark_coords = self.get_top_landmarks()

        left_right = np.zeros([3])
        for i, lm in enumerate(top_landmark_coords):
            left_right[i] = Math.sum_dist_multi_points(lm, [left, right])
        idx = left_right.argmin()
        left_right_lm = top_landmark_coords[idx]

        right_non = np.zeros([3])
        for i, lm in enumerate(top_landmark_coords):
            right_non[i] = Math.sum_dist_multi_points(lm, [right, non])
        idx = right_non.argmin()
        right_non_lm = top_landmark_coords[idx]

        non_left = np.zeros([3])
        for i, lm in enumerate(top_landmark_coords):
            non_left[i] = Math.sum_dist_multi_points(lm, [non, left])
        idx = non_left.argmin()
        non_left_lm = top_landmark_coords[idx]

        return left_right_lm, right_non_lm, non_left_lm

    def plot_landmarks(self):
        sample = np.copy(self.arr)

        indices = self.get_indices()
        drawings = self.drawings()

        top_idx = indices['top_idx']
        bottom_idx = indices['bottom_idx']
        coronaries_idx = indices['coronaries_idx']

        top_slide = np.copy(sample[top_idx])
        bottom_slide = np.copy(sample[bottom_idx])
        coronaries_slide = np.copy(sample[coronaries_idx])
        triangles = drawings['triangles']
        ellipses = drawings['ellipses']
        bottom_triangle = triangles[bottom_idx]
        bottom_ellipse = ellipses[bottom_idx]

        bottom_landmarks = self.bottom_landmarks()
        top_landmarks = self.top_landmarks()
        fig, axis = plt.subplots(2, 1)
        fig.tight_layout()

        cusps = ['left', 'right', 'non']
        for c, coords in enumerate(bottom_landmarks):
            cusp = cusps[c]
            x, y = coords
            cv2.circle(bottom_slide, (x, y), 10, color=2, thickness=-1)
            cv2.putText(bottom_slide, cusp, org=(x - 30, y + 40), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1.3, color=2, thickness=2, lineType=cv2.LINE_AA)
        axis[0].imshow(bottom_slide)
        axis[0].set_title('bottom landmarks')

        top_slide_copy = np.copy(top_slide)
        labels = ['left-right', 'right-non', 'non-left']
        for i, coords in enumerate(top_landmarks):
            label = labels[i]
            x, y = coords
            cv2.circle(top_slide_copy, (x, y), 10, color=2, thickness=-1)
            cv2.putText(top_slide_copy, label, org=(x-30, y+40), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1.3, color=2, thickness=2, lineType=cv2.LINE_AA)
        axis[1].imshow(top_slide_copy)
        axis[1].set_title('top_landmarks')
        plt.savefig(
            FileFolders.folders['global']['shared'] / 'landmarks.png',
            dpi=300)
        
        """ 
        Paper results (need to be removed afterward)
        """
        fig, ax = plt.subplots(1,3)
        ax[0].imshow(np.copy(sample[coronaries_idx]))
        ax[1].imshow(triangles[top_idx])
        ax[2].imshow(triangles[bottom_idx])
        fig.tight_layout()
        plt.savefig(
            FileFolders.folders['global']['shared'] / 'paper_results.png',
            dpi=300)
        
    def export(self):
        indices = self.get_indices()
        top_landmarks = self.top_landmarks()
        bottom_landmarks = self.bottom_landmarks()
        metadata = self.get_metadata()
        top_idx = indices['top_idx']
        bottom_idx = indices['bottom_idx']
        
        
        dx = dy = metadata['dx']
        dz = metadata['dz']

        top_z = top_idx * dz
        bottom_z = bottom_idx * dz

        """
        P4 is pick of left cusp, P5 is on the non coronary cusp and P6 in on the right cusp\
        2- P1 between left and right; P2 between left and None; P3 between right and None       
        """
       
        results = {
            '1': bottom_landmarks[0],
            '2': bottom_landmarks[1],
            '3': bottom_landmarks[2],
            '4': top_landmarks[0],
            '5': top_landmarks[1],
            '6': top_landmarks[2],
        }
             
       
        arr = np.zeros((6, 3))
        for i in range(6):
            if i <= 2:
                arr[i] = results[str(i+1)][0] * dx, results[str(i+1)][1] * dx, bottom_z
            else:
                arr[i] = results[str(i+1)][0] * dx, results[str(i+1)][1] * dx, top_z

        # add p7 as average of all other points
        p7 = np.mean(arr[:3, :], axis=0)
        p7[2] = (top_z + bottom_z)/2
        # p7[2] = top_z
        arr = np.vstack([arr, p7])
        
        print(arr)
        
        df = pd.DataFrame(arr)    
        df.to_csv(files['landmarks'], index=False, header=False, encoding='utf-8')


def main():
    Functions.refresh()
    sample_label = str(lp['labels'][10])
    detector = DetectLandmarks(sample_label)
    results = detector.correct_order()
    

if __name__ == "__main__":
    main()
