import sys
import os
args = sys.argv
from pathlib import Path
this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = Path(os.path.join(this_directory, '..'))
sys.path.append(working_dir)


input_file = "/home/data/input_file.nrrd"


output_dir = '"/home/data/cardiovision_results"'

component = '"aorta"'

if '-v' in args:
    verbose = True
else:
    verbose = False

with open(os.path.join(working_dir, 'utils', 'settings.py'), 'w') as f:
    f.write('import os\n')
    f.write('import sys\n')
    f.write('from pathlib import Path\n')
    f.write('this_directory = os.path.abspath(os.path.dirname(__file__))\n')
    f.write('working_dir = Path(os.path.join(this_directory, ".."))\n')
    f.write('sys.path.append(working_dir)\n')
    f.write('SECRET_KEY = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)\n')
    f.write(f'component = {component}\n')
    f.write(f'input_file = "{input_file}"\n')
    f.write(f'output_dir = {output_dir}\n')
    f.write(f'verbose = {verbose}\n')