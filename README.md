# cardiovision 0.1

## Prequisites
- Install docker on Windows/Linux/Mac: https://docs.docker.com/get-docker
- Only one windows: Install WSL2: https://docs.microsoft.com/en-us/windows/wsl/install

## Preparing data for training and prediction
replace "/home/amir/projects/data" in line 3 of "installing Cardiovision" section with the folder where\
data (for training or prediction) exist.

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
Results will be saved within data/cardiovision_results directory which will be created after successfull\
running of the cardiovision package.

## Installing Cardiovision
### 1- navigate to the main directory of "cardiovision"

>docker build -t cardiovision_image .\
>docker run -d -t -v /home/amir/data:/home/data --name cardiovision_container cardiovision_image /bin/bash\
>docker exec -it cardiovision_container /bin/bash

### 2- run the following commands

>eval "$(conda shell.bash hook)"\
>chmod +x bash_script.sh\
>. /root/miniconda3/etc/profile.d/conda.sh
>./bash_script.sh


## Uninstalling Cardiovision
exit the container using "exit" command. When you are back in the host terminal:
>docker stop cardiovision_container\
>docker rm cardiovision_container\
>docker rmi cardiovision_image
