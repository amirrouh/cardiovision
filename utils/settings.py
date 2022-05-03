import os
import sys
from pathlib import Path
this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = Path(os.path.join(this_directory, '..'))
sys.path.append(working_dir)

component = 'aorta'
verbose = True

SECRET_KEY = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)

if SECRET_KEY:
    if component == 'aorta':
        input_file = f'/home/data/aorta_segmentations/images/ct0.nrrd'
    elif component == 'lv':
        input_file = f'/home/data/lv_segmentations/images/case1_ct.nrrd'
    output_dir =  f'/home/data/cardiovision_results/{component}'

else:
    if component == 'aorta':
        input_file = f'/home/amir/projects/data/aorta_segmentations/images/ct0.nrrd'
    elif component == 'lv':
        input_file = f'/home/amir/projects/data/lv_segmentations/images/case1_ct.nrrd'
    output_dir =  f'/home/amir/projects/data/cardiovision_results/{component}'
