import sys
import os
from pathlib import Path
import subprocess
import shutil

this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = Path(os.path.join(this_directory, '..'))

from config import verbose

conda_envs = Path(os.environ['CONDA_PREFIX']).parents[0]
    
def run(env_path, script, args):
    if sys.platform == 'win32':
        cmd = f"{env_path} {script} {args}"
        os.system(cmd)
    else:
        if verbose:
            subprocess.call([env_path, script, args])
        else:
            result = subprocess.call([env_path, script, args], 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)       
            
def run_module(env, args=""):
    if sys.platform == 'darwin' or sys.platform == 'linux':
        env_path = conda_envs / env / 'bin' / 'python'
    elif sys.platform == 'win32':
        env_path = conda_envs / env / 'python.exe'
    script = working_dir / f"{env}/scripts/run.py"
    
    run(env_path, script, args)
    report = working_dir / env / 'shared'
    shared_files = list(report.glob('*'))
    if len(shared_files) >= 1:
        for file in shared_files:
            if ('pkl' not in str(file)) and ('temp' not in str(file)):
                shutil.copy2(
                    file,
                    working_dir / 'shared'
                )


def run_script(env, script, args=""):
    if sys.platform == 'darwin' or sys.platform == 'linux':
        env_path = conda_envs / env / 'bin' / 'python'
    elif sys.platform == 'win32':
        env_path = conda_envs / env / 'python.exe'

    run(env_path, script, args)


