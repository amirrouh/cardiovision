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

- Note: Make sure the defined files and directories in the "/ui/config.py" file exist and use the proper path format (For unix systems such as macos and linux, use "/" and in windows systems use "\\\\" to refer to the subdirectories.) 

# Using Cardiovision

Navigate to the "/ui" directory and run the following commands

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
>sudo usermod -aG docker $USER
- Verify that the NVIDIA driver is installed in WSL2 by running:
> nvidia-smi
Which should output the graphic card information

## Powered by

|First Image|Second Image|Third Image|
|:-:|:-:|:-:|
|![First Image](https://images.pexels.com/photos/585759/pexels-photo-585759.jpeg?h=750&w=1260)|![Second Image](https://images.pexels.com/photos/1335115/pexels-photo-1335115.jpeg?h=750&w=1260)|!
[Third Image](https://images.pexels.com/photos/1335115/pexels-photo-1335115.jpeg?h=750&w=1260)|