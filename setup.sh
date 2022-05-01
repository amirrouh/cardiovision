#!/bin/zsh

conda init zsh

# Create the required environments
# cardiovision (main env to control the other envs)
eval "$(conda shell.bash hook)"
conda create --name cardiovision python=3.8 -y
conda activate cardiovision
conda install tqdm -y
conda deactivate

# setting up cnn environment
eval "$(conda shell.bash hook)"
conda create --name cnn python=3.6 -y
conda activate cnn
conda install tensorflow-gpu=1.14 -y
conda install keras=2 -y
conda install -c simpleitk simpleitk -y
conda deactiva

# setting up cleanup environment
eval "$(conda shell.bash hook)"
conda create --name cleanup python=3.8 -y
conda activate cleanup
pip install scikit-image vtk scipy SimpleITK
conda deactivate

# setting up landmark environment
eval "$(conda shell.bash hook)"
conda create --name landmark python=3.8 -y
conda activate landmark
conda install -c simpleitk simpleitk -y
conda install matplotlib scipy pandas -y
conda install -c conda-forge opencv -y
conda deactivate

# setting up valve generation environment
eval "$(conda shell.bash hook)"
conda create --name valve python=3.7 -y
conda activate valve
pip install open3d pymeshlab vtk numpy
conda deactivate

# setting up calcification environment
eval "$(conda shell.bash hook)"
conda create --name calcification python=3.8 -y
conda activate calcification
pip install open3d vtk scikit-image trimesh SimpleITK
conda deactivate

# setting up report environment
eval "$(conda shell.bash hook)"
conda create --name report python=3.8 -y
conda activate report
conda install tqdm -y
conda deactivate

# Activate the main env
eval "$(conda shell.bash hook)"
conda activate cardiovision