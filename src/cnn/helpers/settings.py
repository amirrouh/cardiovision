import os
import sys
from pathlib import Path

sys.path.append('..')
from cnn.initialization.create_folders import checkpoints_folder
from main_run.global_settings import input_file, output_dir


component = 'aorta'
n_classes = 2

if sys.platform == "win32":
    input_dir = Path("D:\\cloud\\OneDrive - Mass General Brigham\\projects\\left_heart_segmentation\\data\\"
                     "segmentations\\{}_segmentations\\".format(component))
elif sys.platform == 'darwin':
    input_dir = Path("/Users/amir/OneDrive - Mass General Brigham/projects/left_heart_segmentation/"
                     "data/segmentations/{}_segmentations".format(component))
model_checkpoint = os.path.join(checkpoints_folder, "{}.hdf5".format(component))


input_file = input_file
output_file = os.path.join(output_dir, Path(input_file).name)

