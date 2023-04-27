import os
import sys
from pathlib import Path
this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = Path(os.path.join(this_directory, ".."))
sys.path.append(working_dir)
SECRET_KEY = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)
training_dir = "/home/data/training_data/"
