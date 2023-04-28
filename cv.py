import os
import sys
import platform
import logging
import config as config

input_file = config.input_file

# read images
result = os.popen("docker image ls").readlines()
images = []
for l in result[1:]:
    line = l.strip("\n")
    images.append(line.split()[0])
if len(images) > 1:
    images = images[:-1]

# read containers
result = os.popen("docker ps -a").readlines()
containers = []
for l in result[1:]:
    line = l.strip("\n")
    if 'cv_container' in line:
        containers.append(line.split()[-1])

def install():
    try:
        machine = platform.platform()
        if "macOS" in machine and "arm" in machine:
            # Neccessary environment variable for apple sillicon processors
            os.environ['DOCKER_DEFAULT_PLATFORM'] = "linux/amd64"
        if "cv_image" not in images:
            print('test')
            os.system("docker build -t cv_image .")
        if "cv_container" not in containers:
            if config.GPU:
                os.system(f"docker run --gpus all -d -t --name cv_container -v {config.output_dir}/:/home/data cv_image")
            else:
                os.system(f"docker run -d -t --name cv_container -v {config.output_dir}/:/home/data cv_image")
        if "cv_image" in images and "cv_container" in containers:
            print("Cardiovision is installed successfully")           
        logging.debug("Cardiovision is installed")
    except Exception as e:
        print("Something went wrong, plase try again...")
        logging.error(e)
        return False

def import_data():
    print("Importing, augmenting, and preprocessing the training data ")
    os.system("docker cp config.py cv_container:/home/app/config.py")
    os.system(f"docker cp {config.training_data_directory}/. cv_container:/home/data/training_data")
    os.system("docker exec cv_container bash /home/app/scripts/cardiovision.sh -i")

def train():
    print("Training cardiovision...")
    os.system("docker exec cv_container bash /home/app/scripts/cardiovision.sh -t")

def predict():
    print("copying the input file to the docker container...")
    os.system(f"docker cp {input_file} cv_container:/home/data/input_file.nrrd")
    print("Predicting the outcome based on the trainig data...")
    if config.verbose:
        os.system(f"docker exec cv_container bash /home/app/scripts/cardiovision.sh -p -{config.component} -verbose")
    else:
        os.system(f"docker exec cv_container bash /home/app/scripts/cardiovision.sh -p -{config.component}")
    
    os.system(f"docker cp cv_container:/home/app/shared {config.output_dir}")

    print("prediction completed. Please check the output directory")

def export():
    print("Exporting trainig features...")
    os.system(f"python3 scripts/export.py")

def reset():
    print("Resetting the cardiovision...")
    try:
        if "cv_container" in containers:
            os.system("docker exec cv_container rm -rf /home/data/training_data/*")
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


arg = sys.argv[1]


if arg.upper() == "INSTALL":
    install()
    os.system('docker cp utils/config.py cv_container:/home/app/utils/config.py')
elif arg.upper() == "IMPORT":
    import_data()
elif arg.upper() == "TRAIN":
    train()
elif arg.upper() == "EXPORT":
    export()
elif arg.upper() == "PREDICT":
    predict()
elif arg.upper() == "RESET":
    reset()
    os.system('python cv.py install')
elif arg.upper() == "UNINSTALL":
    uninstall()
