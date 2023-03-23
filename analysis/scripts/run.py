import sys
import os
from pathlib import Path
import distutils.log
import distutils.dir_util
import numpy as np

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from config import output_dir
from analysis.src.helpers import create_folders

# create required folders
create_folders()

results_dir = 

distutils.log.set_verbosity(distutils.log.DEBUG)
distutils.dir_util.copy_tree(
    outputs,
    output_dir,
    update=1,
    verbose=0,
)
