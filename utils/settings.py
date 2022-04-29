import os
import sys
from pathlib import Path
this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = Path(os.path.join(this_directory, '..'))
sys.path.append(working_dir)

component = 'aorta'
verbose = True

if sys.platform == 'win32':
    input_file = 'D:\\cloud\\OneDrive - Mass General Brigham\\projects\\data\\segmentations\\aorta_segmentations\\images\\ct0.nrrd'
elif sys.platform == 'linux':
    if component == 'aorta':
        input_file = f'/mnt/d/cloud/OneDrive - Mass General Brigham/projects/data/segmentations/aorta_segmentations/images/ct0.nrrd'
    elif component == 'lv':
        input_file = f'/mnt/d/cloud/OneDrive - Mass General Brigham/projects/data/segmentations/lv_segmentations/images/case1_ct.nrrd'
    output_dir =  f'/mnt/c/Users/amir/Documents/temp/{component}'
elif sys.platform == 'darwin':
    input_file = '/Users/amir/OneDrive - Mass General Brigham/projects/data/segmentations/aorta_segmentations/images/ct0.nrrd'
    output_dir = '/Users/amir/Documents/temp'