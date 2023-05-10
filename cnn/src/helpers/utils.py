import numpy as np
import SimpleITK as sitk

from scipy import spatial


def resample(image, output_spacing, interplator):
    resample = sitk.ResampleImageFilter()
    input_size = image.GetSize()
    pixel_type = image.GetPixelID()
    input_spacing = image.GetSpacing()
    input_spacing = np.round(input_spacing, 5)
    output_size = [int(np.floor(input_spacing[0] / output_spacing[0] * input_size[0])),
                   int(np.floor(input_spacing[1] / output_spacing[1] * input_size[1])),
                   int(np.floor(input_spacing[2] / output_spacing[2] * input_size[2]))]
    resample.SetInterpolator(interplator)
    resample.SetOutputSpacing(output_spacing)
    resample.SetSize(output_size)
    resample.SetOutputPixelType(pixel_type)
    resample.SetOutputOrigin(image.GetOrigin())
    resample.SetOutputDirection(image.GetDirection())
    return resample.Execute(image)


def pad_crop(image, output_size):
    size = image.GetSize()
    if size[0] < output_size[0]:
        image = pad_image(image, (output_size[0], size[1], size[2]))
    if size[1] < output_size[1]:
        image = pad_image(image, (size[0], output_size[1], size[2]))
    if size[2] < output_size[2]:
        image = pad_image(image, (size[0], size[1], output_size[2]))
    image = crop_image(image, (output_size[0], output_size[1], output_size[2]))
    return image


def crop_image(image, output_size):
    input_size = image.GetSize()
    size_diff = np.subtract(input_size, output_size)
    size_diff[size_diff < 0] = 0
    if np.sum(size_diff) == 0:
        return image
    lower_bound = [int(diff / 2) for diff in size_diff]
    upper_bound = size_diff - lower_bound
    upper_bound = [int(item) for item in upper_bound]
    crop = sitk.CropImageFilter()
    crop.SetLowerBoundaryCropSize(lower_bound)
    crop.SetUpperBoundaryCropSize(upper_bound)
    return crop.Execute(image)


def pad_image(image, output_size):
    input_size = image.GetSize()
    size_diff = np.subtract(output_size, input_size)
    size_diff[size_diff < 0] = 0
    lower_bound = [int(diff / 2) for diff in size_diff]
    upper_bound = size_diff - lower_bound
    upper_bound = [int(item) for item in upper_bound]
    padding = sitk.ConstantPadImageFilter()
    padding.SetPadLowerBound(lower_bound)
    padding.SetPadUpperBound(upper_bound)
    padding.SetConstant(float(np.amin(sitk.GetArrayFromImage(image))))
    return padding.Execute(image)

class SegmentationQualityMetrics:
    """Code taken from https://github.com/hjkuijf/MRBrainS18 with minor refactoring"""

    def __init__(self, labels, test_image, pred_image):
        self.test_image = test_image
        self.pred_image = pred_image
        self.labels = labels
        """
        labels example
        #
        labels = {1: 'Cortical gray matter',
          2: 'Basal ganglia',
          3: 'White matter',
          4: 'White matter lesions',
          5: 'Cerebrospinal fluid in the extracerebral space',
          6: 'Ventricles',
          7: 'Cerebellum',
          8: 'Brain stem',
          # The two labels below are ignored:
          #9: 'Infarction',
          #10: 'Other',
          }
        """

    def get_dice(self):
        """Compute the Dice Similarity Coefficient."""
        dsc = dict()
        for k in self.labels.keys():
            test_nda = sitk.GetArrayFromImage(sitk.BinaryThreshold(self.test_image, k, k, 1, 0)).flatten()
            pred_nda = sitk.GetArrayFromImage(sitk.BinaryThreshold(self.pred_image, k, k, 1, 0)).flatten()
            # similarity = 1.0 - dissimilarity
            # spatial.distance.dice raises a ZeroDivisionError if both arrays contain only zeros.
            try:
                dsc[k] = 1.0 - spatial.distance.dice(test_nda, pred_nda)
            except ZeroDivisionError:
                dsc[k] = None

        return dsc

    def get_hausdorff(self):
        """Compute the 95% Hausdorff distance."""
        hd = dict()
        for k in self.labels.keys():
            l_test_image = sitk.BinaryThreshold(self.test_image, k, k, 1, 0)
            l_pred_image = sitk.BinaryThreshold(self.pred_image, k, k, 1, 0)

            # Hausdorff distance is only defined when something is detected
            statistics = sitk.StatisticsImageFilter()
            statistics.Execute(l_test_image)
            l_test_sum = statistics.GetSum()
            statistics.Execute(l_pred_image)
            l_result_sum = statistics.GetSum()
            if l_test_sum == 0 or l_result_sum == 0:
                hd[k] = None
                continue

            # Edge detection is done by ORIGINAL - ERODED, keeping the outer boundaries of lesions.
            # Erosion is performed in 2D
            e_test_image = sitk.BinaryErode(l_test_image, (1, 1, 0))
            e_pred_image = sitk.BinaryErode(l_pred_image, (1, 1, 0))

            h_test_image = sitk.Subtract(l_test_image, e_test_image)
            h_pred_image = sitk.Subtract(l_pred_image, e_pred_image)

            h_test_nda = sitk.GetArrayFromImage(h_test_image)
            h_pred_nda = sitk.GetArrayFromImage(h_pred_image)

            # Convert voxel location to world coordinates. Use the coordinate system of the test image
            # np.nonzero   = elements of the boundary in numpy order (zyx)
            # np.flipud    = elements in xyz order
            # np.transpose = create tuples (x,y,z)
            # testImage.TransformIndexToPhysicalPoint converts (xyz) to world coordinates (in mm)
            # (Simple)ITK does not accept all Numpy arrays; therefore we need to convert the coordinate
            # tuples into a Python list before passing them to TransformIndexToPhysicalPoint().
            testCoordinates = [self.test_image.TransformIndexToPhysicalPoint(x.tolist()) for x in
                               np.transpose(np.flipud(np.nonzero(h_test_nda)))]
            resultCoordinates = [self.test_image.TransformIndexToPhysicalPoint(x.tolist()) for x in
                                 np.transpose(np.flipud(np.nonzero(h_pred_nda)))]

            # Use a kd-tree for fast spatial search
            def get_distance_from_a_to_b(a, b):
                kdTree = spatial.KDTree(a, leafsize=100)
                return kdTree.query(b, k=1, eps=0, p=2)[0]

            # Compute distances from test to result and vice versa.
            d_test_to_pred = get_distance_from_a_to_b(testCoordinates, resultCoordinates)
            d_pred_to_test = get_distance_from_a_to_b(resultCoordinates, testCoordinates)
            hd[k] = max(np.percentile(d_test_to_pred, 95), np.percentile(d_pred_to_test, 95))

        return hd

    def get_vs(self):
        """Volume similarity.

        VS = 1 - abs(A - B) / (A + B)

        A = ground truth in ML
        B = participant segmentation in ML
        """
        # Compute statistics of both images
        test_stats = sitk.StatisticsImageFilter()
        pred_stats = sitk.StatisticsImageFilter()

        vs = dict()
        for k in self.labels.keys():
            test_stats.Execute(sitk.BinaryThreshold(self.test_image, k, k, 1, 0))
            pred_stats.Execute(sitk.BinaryThreshold(self.pred_image, k, k, 1, 0))

            num = abs(test_stats.GetSum() - pred_stats.GetSum())
            denom = test_stats.GetSum() + pred_stats.GetSum()

            if denom > 0:
                vs[k] = 1 - float(num) / denom
            else:
                vs[k] = None

        return vs

class Parser:
    @staticmethod
    def get_id_from_name(name):
        """ gets any number in the name """
        number_in_name = ""
        for char in name:
            if char.isdigit():
                number_in_name += str(char)
        if number_in_name == "":
            raise 'All images and masks should have a unique number in their file names'
        return number_in_name