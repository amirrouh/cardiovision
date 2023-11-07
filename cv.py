import os
import sys
import platform
import logging
import config as config
import log.log_format as log_format

input_file = config.input_file

# set up log
script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
if (not log_format.set_up_logging(console_log_output="stdout", console_log_level="warning", console_log_color=True,
                        logfile_file="./log/" + script_name + ".log", logfile_log_level="debug", logfile_log_color=False,
                        log_line_template="%(color_on)s[%(asctime)s] [%(threadName)s] [%(levelname)-8s] %(message)s%(color_off)s")):
    print("Failed to set up logging, aborting.")

'''
logging.debug("Debug message example")
logging.info("Info message example")
logging.warning("Warning message example")
logging.error("Error message example")
logging.critical("Critical message example")
'''

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
if len(containers) > 1:
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
    #print("Importing, augmenting, and preprocessing the training data ")
    print(config.training_data_directory)
    logging.info("Importing, augmenting, and preprocessing the training data ")
    print("checkpoint1")
    os.system(f"docker cp {config.training_data_directory}/. cv_container:/home/data/training_data")
    print("checkpoint2")
    os.system("docker exec cv_container bash /home/app/scripts/cardiovision.sh -i")
    print("checkpoint3")

def train():
    #print("Training cardiovision...")
    logging.info("Training cardiovision...")
    os.system("docker exec cv_container bash /home/app/scripts/cardiovision.sh -t")

def predict():
    #print("copying the input file to the docker container...")
    logging.info("copying the input file to the docker container...")
    os.system(f"docker cp {input_file} cv_container:/home/data/input_file.nrrd")
    #print("Predicting the outcome based on the trainig data...")
    logging.info("Predicting the outcome based on the trainig data...")
    if config.verbose:
        os.system(f"docker exec cv_container bash /home/app/scripts/cardiovision.sh -p -{config.component} -verbose")
    else:
        os.system(f"docker exec cv_container bash /home/app/scripts/cardiovision.sh -p -{config.component}")
    
    os.system(f"docker cp cv_container:/home/app/shared {config.output_dir}")

    #print("prediction completed. Please check the output directory")
    logging.info("prediction completed. Please check the output directory")

def export():
    #print("Exporting trainig features...")
    logging.info("Exporting trainig features...")
    os.system(f"python3 scripts/export.py")

def reset():
    #print("Resetting the cardiovision...")
    logging.info("Resetting the cardiovision...")
    try:
        os.system("docker stop cv_container")
        os.system("docker rm cv_container")
    except:
        #print("something went wrong, please try again or uninsall/install cardiovision")
        logging.error("something went wrong, please try again or uninsall/install cardiovision")

def uninstall():
    #print("Uninstalling the cardiovision")
    logging.info("Uninstalling the cardiovision")
    try:
        os.system("docker system prune -a")
        #print("Cardiovision successfully ininstalled.")
        logging.info("Cardiovision successfully ininstalled.")
    except:
        #print("Something weng wrong please try to remove cv_image and cv_container using docker app")
        logging.error("Something weng wrong please try to remove cv_image and cv_container using docker app")


arg = sys.argv[1]


if arg.upper() == "INSTALL":
    install()
elif arg.upper() == "IMPORT":
    import_data()
elif arg.upper() == "TRAIN":
    train()
elif arg.upper() == "EXPORT":
    export()
elif arg.upper() == "PREDICT":
    predict()
elif arg.upper() == "UNINSTALL":
    uninstall()
