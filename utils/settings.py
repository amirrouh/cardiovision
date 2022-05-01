import os
import sys
from pathlib import Path
this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = Path(os.path.join(this_directory, '..'))
sys.path.append(working_dir)

component = 'aorta'
verbose = True

# data_dir = "/mnt/d/cloud/OneDrive - Mass General Brigham/projects/data"

if component == 'aorta':
    input_file = '/home/amir/projects/data/segmentations/aorta_segmentations/images/ct0.nrrd'
elif component == 'lv':
    input_file = '/home/amir/projects/data/segmentations/lv_segmentations/images/case1_ct.nrrd'
output_dir =  f'/home/amir/projects/data/segmentations/aorta_segmentations/cardiovision_results/{component}'
