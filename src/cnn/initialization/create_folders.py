import os
from pathlib import Path

folders = list()

current_root = Path(os.path.abspath(os.path.dirname(__file__)))
project_root = current_root/'..'

intermediate_folder = os.path.join(project_root, 'intermediate')
folders.append(intermediate_folder)

data_folder = os.path.join(intermediate_folder, 'data')
folders.append(data_folder)

sheets_folder = os.path.join(data_folder, 'sheets')
folders.append(sheets_folder)

#
images_folder = os.path.join(data_folder, 'images')
folders.append(images_folder)
#
arrays_folder = os.path.join(data_folder, 'arrays')
folders.append(arrays_folder)

# models folder is where we store trained deep learning models
models_folder = os.path.join(intermediate_folder, 'models')
folders.append(models_folder)

snaps_folder = os.path.join(intermediate_folder, 'snaps')
folders.append(snaps_folder)

shared_dir = os.path.join(project_root, 'shared')
folders.append(shared_dir)

checkpoints_folder = os.path.join(project_root, 'checkpoints')

if __name__ == '__main__':
    for folder in folders:
        if not os.path.isdir(folder):
            os.mkdir(folder)
        else:
            print('folder {} exists.'.format(folder))
