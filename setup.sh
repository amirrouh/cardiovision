#!/bin/zsh

conda init zsh

# # Create the required environments
# # cardiovision (main env to control the other envs)
# conda create --name cardiovision python=3.8 -y
# conda activate cardiovision
# conda install tqdm -y
# conda deactivate

# # setting up cnn environment
# conda create --name cnn python=3.6 -y
# conda activate cnn
# conda install tensorflow-gpu=1.14 -y
# conda install keras -y
# conda install -c simpleitk simpleitk -y
# conda deactivate

# # setting up cleanup environment
# conda create --name cleanup python=3.8 -y
# conda activate cleanup
# pip install scikit-image vtk scipy
# conda deactivate

# # setting up landmark environment
# conda create --name landmark python=3.8 -y
# conda activate landmark
# conda install -c simpleitk simpleitk -y
# conda install matplotlib scipy pandas -y
# conda install -c conda-forge opencv -y
# conda deactivate

# # setting up valve generation environment
# conda create --name valve python=3.7 -y
# conda activate valve
# pip install open3d pymeshlab vtk numpy
# conda deactivate

# setting up calcification environment
conda create --name calcification python=3.8 -y
conda activate calcification
pip install open3d vtk scikit-image trimesh SimpleITK
conda deactivate

# setting up report environment
conda create --name report python=3.8 -y
conda activate report
conda install tqdm -y
conda deactivate