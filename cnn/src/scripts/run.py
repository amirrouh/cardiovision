import sys
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from utils.helpers import run_script, working_dir

args = sys.argv

"""
initialization
    creat_folders
preprocessing
    resample
    split
    datagen
train
    train
    val_pred
    ensample_preds
analysis
    cv_performance
postprocessing
    predict
    cleanup_geometry
"""

print('cnn is running')
if '-predict' in args:
    run_script('cnn', working_dir/'cnn'/'postprocessing'/'predict.py')
    run_script('cleanup', working_dir/'cnn'/'postprocessing'/ 'cleanup.py')

