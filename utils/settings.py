import os
import sys
from pathlib import Path
this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = Path(os.path.join(this_directory, ".."))
sys.path.append(working_dir)
SECRET_KEY = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)
component = "aorta"
input_file = "/home/data/input_file.nrrd"
output_dir = "/home/data/cardiovision_results"
verbose = False
