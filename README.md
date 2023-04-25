# Cardiovision User Manual
Cardiovision (CV) is a user-friendly cross-platform application for medical image segmentation using deep learning. CV is  successfully tested on Windows, Linux, and MacOS (intel and apple sillicon processor).
# Prequisites
- Install docker on Windows/Linux/Mac: https://docs.docker.com/get-docker
- On WINDOWS machine use a text editor make sure the dockerfile and bash_script.sh files have linux format (LF) line ending
- At least 30 GB free storage for cardiovision.
- At least 16 GB RAM is recommended.
- Nvidia GPU is not necessary but highly recommended.


# Directory Structure For Training
Both images and labels should be 512*512 slides saved as nrrd file:

* path to trainig data
    * images
        * ct01.nrrd
        * ct02.nrrd
        * ...
    * labels
        * segmented1.nrrd
        * segmented2.nrrd
        * ...

Note that images and labels have some numeric character to relate the two. You can use any formatting\
as long as the numbers are the same for any corresponding image and label.

# Install Cardiovision
>python cv.py install

- Note: If the following ERROR is encuntered: "...cv_image, repository does not exist or may require 'docker login': denied: requested access to the resource is denied...", run the following command in terminal: "rm  ~/.docker/config.json", then try installing the CardioVision again

- Note: If the following ERROR is encountered: ... docker login: denied", run the following commands in the terminal before installing the CV.
> export DOCKER_BUILDKIT=0

> export COMPOSE_DOCKER_CLI_BUILD=0


- Note: Make sure the defined files and directories in the "/ui/config.py" file exist and use the proper path format (For unix systems such as macos and linux, use "/" and in windows systems use "\\\\" to refer to the subdirectories.) 

- Making sure the docker image and containers are installed and running properly. This can be done either within the docker desktop app or via the command line. For examle, for a unix terminal (MAC, LINUX, Windows WSL2) the command "docker ps" should return the info including the "cv_container" name.

# Using Cardiovision
### Before running
- Make sure the cv_container is running which can be seen in the output of the following command:
> docker ps

if not running, run the following command:
> docker start cv_container

if error "Error response from daemon: error while creating mount source path..." occured:
> restart the docker application
d
### Edit the configuration file properly:

- output_directory: directory in which the results will be saved
- training_data_directory: path to the trainig data
- input_file: new nrrd file based on which the predictions will be done
- component: predicting component which is "aorta" for digital twin and "lv" for left venctricle, more components can be added in future. Also, customly trained components will be added here.
- verbose: if "True", prints out the output of the python console useful for debugging the code
- GPU: if True, it will use the CUDA enabled NVIDIA GPU. If not, it will use the CPU

### Import/Preprocess training data
>python cv.py import

### Training using costum dataset
>python cv.py train

### Predicting a new case
>python cv.py predict

### Exporting training features
>python cv.py export

# Reset/Uninstall Cardiovision
### Resetting Cardiovision
>python cv.py reset

### Uninstalling Cardiovision
>python cv.py uninstall

# Advanced manipulations
### To login to the docker container:
>docker exec -it cv_container /bin/bash

### To change prediction component
>change component variable in "/root/scripts/generate_settings.py" file

### To make the changes permanent
>docker commit cv_container cv_image

### Clean previous training data
>docker exec cv_container rm -rf /home/data/training_data/*

### Enabling Cuda Accelarion support for Faster training and predictions using docker on Windows Subsystem for Linux (WSL2)
- Install the latest nvidia driver
- Install WSL2
- Install docker on windows and Integrate it with WSL2
- Add your WSL2 username to the docker group:
> sudo usermod -aG docker $USER

or if another windows account is trying to use the docker, then run the following code:

> net localgroup docker-users "your-user-id" /ADD

- Verify that the NVIDIA driver is installed in WSL2 by running:
> nvidia-smi
Which should output the graphic card information

## How to Add a Module to CardioVision
- create a folder in the root directory: (i.e. cardiovision/new_module)
- create two subdirectories: "scripts" and "src"
- run.py file within the scriprt dir including a single function to run the module
- copy the module source code within the src subdirectory
- edit cv/bash_script.sh and add the conda environment for the new module according using other modules and template.