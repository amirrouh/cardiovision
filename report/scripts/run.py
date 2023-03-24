from pathlib import Path
import sys
import os
import shutil

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from utils.io import FileFolders, Functions
from config import output_dir

print('exporting the results...')
Functions.sync(Path(FileFolders.folders['global']['shared']), Path(output_dir))

shutil.copytree(FileFolders.folders['global']['shared'], Path(output_dir), dirs_exist_ok=True)