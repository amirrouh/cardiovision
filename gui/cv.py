import os
import gui.config as config
import sys
import platform
import logging

# read images
result = os.popen("docker image ls").readlines()
images = []
for l in result[1:]:
    line = l.strip("\n")
    images.append(line.split()[0])
images = images[:-1]

# read containers
result = os.popen("docker ps -a").readlines()
containers = []
for l in result[1:]:
    line = l.strip("\n")
    containers.append(line.split()[-1])

def install():
    try:
        machine = platform.platform()
        if "macOS" in machine and "arm" in machine:
            # Neccessary environment variable for apple sillicon processors
            os.environ['DOCKER_DEFAULT_PLATFORM'] = "linux/amd64"
        if "cv_image" not in images:
            os.system("docker build -t cv_image .")
        if "cv_container" not in containers:
            os.system(f"docker run --gpus all -d -t --name cv_container -v {config.output_directory}:/home/data cv_image")
        if "cv_image" in images and "cv_container" in containers:
            print("Cardiovision is installed successfully")
        else:
            print("Something went wrong, plase try again...")
        logging.debug("Cardiovision is installed")
    except Exception as e:
        logging.error(e)
        return False

def import_data():
    print("Copying, augmenting, and preprocessing the training data ")
    os.system(f"docker cp {config.training_data_directory} cv_container:/home/data/training_data")
    os.system("docker exec cv_container bash /home/app/scripts/cardiovision.sh -i")

def train():
    print("Training cardiovision...")
    os.system("docker exec cv_container bash /home/app/scripts/cardiovision.sh -t")

def predic():
    print("copying the input file to the docker container...")
    os.system(f"docker cp {config.input_file} cv_container:/home/data/input_file.nrrd")
    print("Predicting the outcome based on the trainig data...")
    if config.verbose:
        os.system(f"docker exec cv_container bash /home/app/scripts/cardiovision.sh -p -{config.component} -verbose")
    else:
        os.system(f"docker exec cv_container bash /home/app/scripts/cardiovision.sh -p -{config.component}")
    print("prediction completed. Please check the output directory")

def export():
    print("Exporting trainig features...")
    os.system(f"python3 io.py -export -results {config.output_directory}")

def reset():
    print("Resetting the cardiovision...")
    try:
        os.system("docker stop cv_container")
        os.system("docker rm cv_container")
    except:
        print("something went wrong, please try again or uninsall/install cardiovision")

def uninstall():
    print("Uninstalling the cardiovision")
    try:
        os.system("docker system prune -a")
        print("Cardiovision successfully ininstalled.")
    except:
        print("Something weng wrong please try to remove cv_image and cv_container using docker app")

def main():
    print("success")
    

if __name__ == "__main__":
    main()




