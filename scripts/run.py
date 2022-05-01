import os
import sys
import shutil
from pathlib import Path

from tqdm import tqdm

this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = os.path.join(this_directory, '..')
sys.path.append(working_dir)

from utils.io import Functions
from utils.helpers import run_module
from utils.io import FileFolders
from utils.settings import component, output_dir

excludes = [
    FileFolders.folders['global']['shared'],
    FileFolders.folders['cnn']['shared'],
]

Functions.refresh()

if component == 'aorta':
    runs = {
        'cnn': '-predict',
        # 'landmark': '',
        # 'valve': '',
        'report': '',
    }
elif component == 'lv':
    runs = {
        'cnn': '-predict',
        'report': '',
    }
    
pbar = tqdm(runs.keys(), desc='Left heart aparatus is being generated...')
for r in pbar:
    pbar.set_description(f'Left heart aparatus is being generated -> {r} modules is running...')

    run_module(r, runs[r])