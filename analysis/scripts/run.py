import sys
import os
from pathlib import Path
import distutils.log
import distutils.dir_util

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from utils.io import FileFolders
from config import input_file, output_dir
from analysis.src.core import split

outputs = Path("dev/cardiovision_results/cardiovision_results")

split(outputs)

distutils.log.set_verbosity(distutils.log.DEBUG)
distutils.dir_util.copy_tree(
    outputs,
    output_dir,
    update=1,
    verbose=0,
)


