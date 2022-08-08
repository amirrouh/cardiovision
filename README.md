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

## Note
To login to the docker container:
>docker exec -it cv_container /bin/bash

## RUN Cardiovision
In the main directory, run the following commands:
>docker build -t cv_image .\
>docker run -d -t --name cv_container -v <output_directory>:/home/data cv_image\
>docker cp <input_file_path> cv_container:/home/data/input_file.nrrd\
>docker exec cv_container bash /home/app/scripts/cardiovision.sh -p


## Removing Cardiovision
exit the container using "exit" command. When you are back in the host terminal:
>docker stop cv_container\
>docker rm cv_container\
>docker rmi cv_image

## Remove all Docker Images/Containers
>dockers system prune -a
