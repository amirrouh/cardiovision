import sys
from pathlib import Path
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from utils.helpers import run_script
from utils.io import working_dir

args = sys.argv

if '-predict' in args:
    run_script('cnn', working_dir /'cnn'/ 'src' / 'postprocessing'/'predict.py')
    run_script('cleanup', working_dir/'cnn'/ 'src' / 'postprocessing'/ 'cleanup.py')