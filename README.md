# cardiovision 0.1

## Prequisites
- Install docker on Windows/Linux/Mac: https://docs.docker.com/get-docker
- Only on windows: Install WSL2: https://docs.microsoft.com/en-us/windows/wsl/install

## Preparing data for training and prediction
data directory structure should be similar to the followings where "images" directory contains the nrrd\
files of the raw images and "labels" directory contains the nrrd files of the segmented images. Both\
images and labels nrrd files should have at least one numeric character to show relation between each\
image and corresponding label, for example:

|--data\
|-------images\
|---------- ct01.nrrd\
|---------- ct02.nrrd
>>...

|-------labels\
|---------- segmented1.nrrd\
|---------- segmented2.nrrd

### Note:
Results will be saved within data/cv_results directory which will be created after successfull\
running of the cardiovision package.

## Installing Cardiovision
### 1- navigate to the main directory of "cardiovision"

>docker build -t cv_image .\
>docker run -d -t -v /home/amir/data:/home/data --name cv_container cv_image /bin/bash\
>docker exec -it cv_container /bin/bash


## Uninstalling Cardiovision
exit the container using "exit" command. When you are back in the host terminal:
>docker stop cv_container\
>docker rm cv_container\
>docker rmi cv_image

## User Manual

### RUN
>docker run -d -t --name cv_container -v <output_directory>:/home/data cv_image\
>docker cp <input_file_path> cv_container:/home/data/input_file.nrrd\
>docker exec cv_container bash /home/app/scripts/cardiovision.sh -p

### Example:
>docker run -d -t --name cv_container -v /mnt/c/Users/amir/Documents:/home/data cv_image\
>docker cp /home/amir/data/aorta_segmentations/images/ct0.nrrd cv_container:/home/data/input_file.nrrd\
>docker exec cv_container bash /home/app/scripts/cardiovision.sh -p