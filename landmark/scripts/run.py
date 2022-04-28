from importlib.machinery import FileFinder
import sys
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

args = sys.argv

from landmark.src.core import DetectLandmarks
from utils.io import FileFolders

aorta_smoothed_nrrd = str(FileFolders.folders['global']['shared'] / 'predicted_smoothed.nrrd') # path to sample aorta segmented
detector = DetectLandmarks(aorta_smoothed_nrrd)
detector.plot_landmarks()
detector.export()
