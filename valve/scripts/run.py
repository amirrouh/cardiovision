import os
import sys
import shutil
from pathlib import Path


this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from valve.src.core import AVgenerator
from utils.io import FileFolders


#Initiate class to generate cusps
generator=AVgenerator()
generator.generateModel()

shell_dir = FileFolders.folders['valve']['shell']
files = list(shell_dir.glob('*complete*'))
for file in files:
    shutil.copy2(str(file), FileFolders.folders['global']['valve_cusps'])

shutil.copy2(str(FileFolders.folders['valve']['pointcloud'] / 'landmark_test_pc.ply'),
             str(FileFolders.folders['global']['shared'] / 'landmarks.ply'))
