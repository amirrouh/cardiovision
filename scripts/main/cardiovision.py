import subprocess
from pathlib import Path
import shutil
import os
import sys

args = sys.argv

# input parameters
input_file_path=Path(args[2])
output_path=Path(args[3])
component = args[4]

_this_path = os.path.dirname(os.path.realpath(__file__))
_temp_directory = output_path/'temp'
_assembly_path = output_path/'assembly'

def _createFolder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    folder_path.mkdir(parents=True, exist_ok=True)   

def _copy(src, dest):
    try:
        #if path already exists, remove it before copying with copytree()
        if os.path.exists(dest):
            shutil.rmtree(dest)
            shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(source_dir_prompt, destination_dir_prompt)
        else:
            print('Directory not copied. Error: %s' % e)

def _cleanDirectoryContent(directory):
    # Empty temp folder for aorta
    folder = str(directory)
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def createTempDirectory():
    _createFolder(_temp_directory)

def getContainersInfo():
    """returns: number of existing containers, number of running containers"""
    # get number of existing contaienrs
    process=subprocess.Popen(['docker', 'ps', '-a', '--format', '"{{.Names}}"'], stdout=subprocess.PIPE)
    std_out, str_err = process.communicate()
    containers = std_out.decode()
    n_of_exist_containers = len(containers.splitlines())
    # number of running containers
    process=subprocess.Popen(['docker', 'ps', '--format', '"{{.Names}}"'], stdout=subprocess.PIPE)
    std_out, str_err = process.communicate()
    containers = std_out.decode()
    n_of_running_containers = len(containers.splitlines())
    return n_of_exist_containers, n_of_running_containers

def removeContainers():
    n_of_exist_containers, _ = getContainersInfo()
    if n_of_exist_containers > 0:
        print('removing previous docker containers...')
        subprocess.run(['sh', f'{_this_path}/bash_scripts/remove_containers.sh'])
        print('\n')

def startFreshContainer():
    print('Starting a fresh docker container...')
    subprocess.run(['sh', f'{_this_path}/bash_scripts/initiate_containers.sh', str(output_path), str(input_file_path)])
    print('\n')

def reconstructLV():
    subprocess.run(['docker', 'exec', 'cv_container', 'bash', '/home/app/scripts/cardiovision.sh', '-p', '-lv'])

def moveLV():
    lv_path = output_path/'lv'
    lv_path.mkdir(parents=True, exist_ok=True)
    _copy(_temp_directory, lv_path)

def reconstructAorta():
    subprocess.run(['docker', 'exec', 'cv_container', 'bash', '/home/app/scripts/cardiovision.sh', '-p', '-aorta'])

def moveAorta():
    aorta_path = output_path/'aorta'
    aorta_path.mkdir(parents=True, exist_ok=True)
    _copy(_temp_directory, aorta_path)

def assembly():
    _createFolder(_assembly_path)
    # copy aorta
    shutil.copy(output_path/'aorta'/'cardiovision_results'/'predicted.stl', _assembly_path/'aorta.stl')

    # copy valves
    shutil.copy(output_path/'aorta'/'cardiovision_results'/'valve_cusps'/'L_complete_cusp_pymeshlab.ply', _assembly_path/'left_cusp.ply')
    shutil.copy(output_path/'aorta'/'cardiovision_results'/'valve_cusps'/'NC_complete_cusp_pymeshlab.ply', _assembly_path/'non_coronary_cusp.ply')
    shutil.copy(output_path/'aorta'/'cardiovision_results'/'valve_cusps'/'R_complete_cusp_pymeshlab.ply', _assembly_path/'right_cusp.ply')

    # copy left ventricle
    shutil.copy(output_path/'lv'/'cardiovision_results'/'predicted.stl', _assembly_path/'lv.stl')

def cleanUp():
    print('\nCleaning up...\n')
    shutil.rmtree(_temp_directory)
    if component == "lv":
        shutil.rmtree(output_path/'lv')
    elif component == "aorta":
        shutil.rmtree(output_path/'aorta')

if __name__=="__main__":
    createTempDirectory()

    if component == "lv":
        removeContainers()
        startFreshContainer()
        reconstructLV()
        moveLV()

    elif component == "aorta":
        removeContainers()
        startFreshContainer()
        reconstructAorta()
        moveAorta()

    cleanUp()
