# cardiovision $v1$

## Prequisites
Install docker on Windows/Linux/Mac: https://docs.docker.com/get-docker\
Only one windows: Install WSL2: https://docs.microsoft.com/en-us/windows/wsl/install

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
|---------- ct02.nrrd\
>>...

|-------labels\
|---------- segmented1.nrrd\
|---------- segmented2.nrrd

Note:
> results will be saved within data/cardiovision_results directory which will be created after successfull\
running of the cardiovision package.

## Installing Cardiovision
navigate to the main directory of "cardiovision"\
docker build -t cardiovision_image .\
docker run -d -t -v /home/amir/projects/data:/home/data --name cardiovision_container cardiovision_image\
docker exec -it cardiovision_container /bin/bash\
eval "$(conda shell.bash hook)"

## Uninstalling Cardiovision
docker stop cardiovision_container\
docker rm cardiovision_container\
docker rmi cardiovision_image
