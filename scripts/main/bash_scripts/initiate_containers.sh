#!/bin/bash

# create a contrainer
docker run -d -t --name cv_container -v $1/temp:/home/data cv_image\

# copy the input file
docker cp $2 cv_container:/home/data/input_file.nrrd