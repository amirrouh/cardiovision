# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 09:37:19 2022

@author: rz445
"""
import os.path
import sys
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from cnn.initialization.create_folders import shared_dir
from main_run.global_settings import shared_dir

import nrrd
import numpy as np
from skimage import filters
from skimage.morphology import ball
from skimage.measure import label
from scipy import ndimage

input_path = os.path.join(shared_dir, 'predicted.nrrd')
output_path = os.path.join(shared_dir, 'predicted_smoothed.nrrd')

# def cleanup_geometry(input_path, output_path):

""" Smoothens and closes holes and retains only largest island in .nrrd file

Args:
    param1 (str): input path (with .nrrd extension)
    param2 (str): output path (with .nrrd extension)

Returns:
    nrrd file: Located at the output path specified
"""

# Opens the image and header file. Header will be kept for saving later
raw, header = nrrd.read(input_path, index_order='C')

raw = np.array(raw)  # Convert to numpy for faster computations
threshold = 0.1  # Threshold value. Anything below will be background
binary_mask = np.where(raw > threshold, 1, 0)  # Convert to binary array

# Remove some of the small holes in the image
binary_mask = ndimage.binary_closing(binary_mask, structure=np.ones((5, 5, 5)))

# Apply a median filter to the image
img = filters.median(binary_mask, ball(3))

# Process to keep only the largest connected component
labels = label(img)  # All seperated labels
assert (labels.max() != 0)
largest_label = labels == np.argmax(np.bincount(labels.flat)[1:]) + 1  # Largest label
img = largest_label.astype(int)  # Convert from bool to int

img = filters.gaussian(img, sigma=1)  # Slight gaussian filter to smoothen image
img = np.where(img > 0, 1, 0)  # Revert back to binary after smoothing operation

print(np.max(img))
print(np.min(img))
print(np.shape(img))
nrrd.write(output_path, img, index_order='C', header=header)