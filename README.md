# cardiovision 0.1 for the 1st time

## Prequisites
- Install docker on Windows/Linux/Mac: https://docs.docker.com/get-docker
- The code is tested successfully on windows and linux
## Directory Structure For Training
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
as long as the numbers are the same for corresponding image and label.

## Install Cardiovision
Navigate to the root directory where Dockerfile exists:
>docker build -t cv_image .

>docker run -d -t --name cv_container -v <output_directory>:/home/data cv_image

## Run Cardiovision

### Train
- copying training data
>docker cp <training_data_directory> cv_container:/home/data/training_data
- prepare for training
>docker exec cv_container bash /home/app/scripts/cardiovision.sh -i
- training
>docker exec cv_container bash /home/app/scripts/cardiovision.sh -t

### Predict
Navigate to the scripts/main, and run:
>python cardiovision.py <input_nrrd_file_path> <output_dir> <component_to_be_predicted>

## Uninstall Cardiovision
exit the container using "exit" command. When you are back in the host terminal:
>docker stop cv_container\
>docker rm cv_container\
>docker rmi cv_image

## Remove all Docker Images/Containers
>dockers system prune -a

## Note
### To login to the docker container:
>docker exec -it cv_container /bin/bash

### To change prediction component
>change component variable in "/root/scripts/generate_settings.py" file

### To make the changes permanent
>docker commit cv_container cv_image

### Clean previous training data
>docker exec cv_container rm -r /home/data/training_data/*
