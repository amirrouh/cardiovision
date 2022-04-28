import numpy as np
import cv2


class Math:
    @staticmethod
    def pop_zeros(items):
        while items[-1] == 0:
            items.pop()
        return items

    @staticmethod
    def aorta_cross_section_area(slides):
        areas = []
        for s in slides:
            aorta_area = np.count_nonzero(s)
            areas.append(aorta_area)
        areas_normalized = [i / np.max(areas) for i in areas]
        return areas_normalized

    @staticmethod
    def calc_distance(p0, p1):
        return np.sqrt((p0[0]-p1[0])**2 + (p0[1]-p1[1])**2)

    @staticmethod
    def calc_normalize(arr, t_min, t_max):
        norm_arr = []
        diff = t_max - t_min
        diff_arr = max(arr) - min(arr)
        for i in arr:
            temp = (((i - min(arr))*diff)/diff_arr) + t_min
            norm_arr.append(temp)
        return norm_arr

    @staticmethod
    def calc_avg_slope(arr, window):
        """
        calculated the slope of the average fitted line though window of items
        returns a list of slopes for fitted lines at each point for a given window
        """
        slope = []
        for i in range(len(arr)-window):
            s, _ = np.polyfit(range(len(arr))[i:i+window], arr[i:i+window], 1)
            slope.append(s)
        return slope

    @staticmethod
    def line_from_points(point1, point2):
        """
        returns m,b for (mx + b) line equation for the line
        """
        m = (point2[1] - point1[1])/(point2[0] - point1[0])
        b = (point1[1] - m * point1[0])
        return m, b

    @staticmethod
    def distance_point_line(point, m, p):
        """
        line passing "p" with slope of "m" in format of ax + by + c = 0 equation =>:
        y - p[1] = m * (x - p[0])
        m * x - y + (p[1] - m * p[0]) = 0
        """
        a = m
        b = -1
        c = p[1] - m * p[0]

        d = np.abs(a * point[0] + b * point[1] + c) / (np.sqrt(a ** 2 + b ** 2))
        return d

    @staticmethod
    def sum_dist_multi_points(reference_point: tuple, points_list: list):
        """
        Calculates summations of distances from reference point to a list of multiple points

        Args:
            reference_point: the reference point coordinate (e.g. (4, 6))
            points_list: list of other points. e.g. [(3,2), (4,1), (2,9)]

        Returns:
            the summation of distances
        """
        d = []
        for p in points_list:
            d.append(Math.calc_distance(reference_point, p))

        d = np.array(d)
        return d.sum()


class Image:
    @staticmethod
    def keep_largest(img):
        """ Only keeps the largest component

        img: input binary image

        returns: output binary image with only largest component
        """

        img = img.astype(np.uint8)

        # find all your connected components (white blobs in your image)
        nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(img, connectivity=8)
        # connectedComponentswithStats yields every seperated component with information on each of them, such as size
        # the following part is just taking out the background which is also considered a component, but most of the time we don't want that.
        sizes = stats[1:, -1];
        nb_components = nb_components - 1

        # minimum size of particles we want to keep (number of pixels)
        # here, it's a fixed value, but you can set it as you want, eg the mean of the sizes or whatever
        min_size = 1000

        # your answer image
        img2 = np.zeros((output.shape))
        # for every component in the image, you keep it only if it's above min_size
        for i in range(0, nb_components):
            if sizes[i] == max(sizes):
                img2[output == i + 1] = 1

        img2 = img2.astype(np.uint8)
        return img2

    @staticmethod
    def draw_circles(slides):
        """
        slides: ndarray
        shape: (number_of_slices, nx, ny)
        """
        circles = []
        similarity_ratio = []

        for s in slides:
            aorta = np.copy(s)
            cnts = cv2.findContours(s, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            (x, y), r = cv2.minEnclosingCircle(cnts[0])
            center = (int(x), int(y))
            color = 1
            thickness = 2
            circles.append(cv2.circle(s, center, int(r), color, thickness))
            circle_area = np.pi * r ** 2
            aorta_area = np.count_nonzero(aorta)
            similarity_ratio.append(1 - abs(circle_area - aorta_area) / circle_area)

        return circles, similarity_ratio

    @staticmethod
    def draw_triangles(slides):
        """
        slides: ndarray
        shape: (number_of_slices, nx, ny)
        """
        triangles = []
        similarity_ratio = []
        equilateral_ratio = []  # 1 for fully equilateral
        midpoints = []
        centroids = []
        edges_list = []
        coords_of_min_angle_vertex = []
        for s in slides:
            aorta = np.copy(s)
            cnts = cv2.findContours(s, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            _, points = cv2.minEnclosingTriangle(cnts[0])
            points = np.array(points).reshape(3, 2).astype(int)
            color = 1
            thickness = 2
            p0 = tuple(points[0])
            p1 = tuple(points[1])
            p2 = tuple(points[2])
            x0, y0 = p0
            x1, y1 = p1
            x2, y2 = p2
            cv2.line(s, p0, p1, thickness)
            cv2.line(s, p1, p2, thickness)
            cv2.line(s, p2, p0, thickness)
            triangles.append(s)
            aorta_area = np.count_nonzero(aorta)
            triangle_area = (1 / 2) * abs(x0 * (y1 - y2) + x1 * (y2 - y0) + x2 * (y0 - y1))
            similarity_ratio.append(1 - abs(triangle_area - aorta_area) / triangle_area)
            l0 = Math.calc_distance(p0, p1)
            l1 = Math.calc_distance(p1, p2)
            l2 = Math.calc_distance(p0, p2)
            # calculate normalized variance
            edges = np.array([l0, l1, l2])
            equilateral = np.var(edges)
            equilateral_ratio.append(equilateral)
            # calculate centroid
            x_c = (1 / 3) * (x0 + x1 + x2)
            y_c = (1 / 3) * (y0 + y1 + y2)
            _centroid = (int(x_c), int(y_c))
            # calculate mid points
            mid_point_1 = (int((1 / 2) * (x0 + x1)), int((1 / 2) * (y0 + y1)))
            mid_point_2 = (int((1 / 2) * (x1 + x2)), int((1 / 2) * (y1 + y2)))
            mid_point_3 = (int((1 / 2) * (x0 + x2)), int((1 / 2) * (y0 + y2)))
            _midpoints = [mid_point_1, mid_point_2, mid_point_3]
            midpoints.append(_midpoints)
            centroids.append(_centroid)
            edges_list.append([(x0, y0), (x1, y1), (x2, y2)])
            # find the coords of vertex with the least angle value
            elong_0 = Math.calc_distance(_centroid, points[0, :])
            elong_1 = Math.calc_distance(_centroid, points[1, :])
            elong_2 = Math.calc_distance(_centroid, points[2, :])
            idx = np.argmin([elong_0, elong_1, elong_2])
            points_list = [points[0, :], points[1, :], points[2, :]]
            coords_of_min_angle_vertex.append(tuple(points_list[idx]))

        equilateral_ratio_norm = Math.calc_normalize(equilateral_ratio, 0, 1)

        return triangles, similarity_ratio, equilateral_ratio_norm, centroids, midpoints, edges_list, coords_of_min_angle_vertex

    @staticmethod
    def draw_ellipses(slides):
        """
        slides: ndarray
        shape: (number_of_slices, nx, ny)
        """
        ellipses = []
        ellipses_params = []
        eccentricity_list = []
        angle_list = []
        for i, s in enumerate(slides):
            aorta = np.copy(s)
            cnts = cv2.findContours(s, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            boundary = cnts[0].reshape(-1, 2)

            ellipse = cv2.fitEllipse(boundary)
            _, (a, b), angle = ellipse
            ellipses_params.append(ellipse)
            color = (255, 0, 0)
            ellipses.append(cv2.ellipse(s, ellipse, color, 1))

            # calculate ratio of a/b elongation
            eccentricity = np.sqrt(np.abs(1 - b ** 2 / a ** 2))
            eccentricity_list.append(eccentricity)
            angle_list.append(angle / 180)
        return ellipses, ellipses_params, eccentricity_list, angle_list

    @staticmethod
    def aorta_cross_section_area(slides):
        areas = []
        for s in slides:
            aorta_area = np.count_nonzero(s)
            areas.append(aorta_area)
        areas_normalized = [i / np.max(areas) for i in areas]
        return areas_normalized


