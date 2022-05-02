# cardiovision

## Intall

docker build -t cardiovision_image .
docker run -d -t -v /home/amir/projects/data:/home/data --name cardiovision_container cardiovision_image
docker exec -it cardiovision_container /bin/sh
<!-- eval "$(conda shell.bash hook)" -->

## Uninstall
docker stop cardiovision_container
docker rm cardiovision_container
docker rmi cardiovision_image