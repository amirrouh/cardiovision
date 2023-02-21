import os
import platform
import sys
import logging
from pathlib import Path

this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = Path(os.path.join(this_directory, '..'))
sys.path.append(working_dir)


root_logger= logging.getLogger(__name__)
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler('cardiovision.log', 'a', 'utf-8')
handler.setFormatter(logging.Formatter("%(levelname)s:%(asctime)s | %(message)s"))
root_logger.addHandler(handler)


class CardioVision:
    @staticmethod
    def install(output_directory):
        images = Docker.images()
        containers = Docker.containers()
        try:
            os.chdir(working_dir)
            machine = platform.platform()
            if "macOS" in machine and "arm" in machine:
                # Neccessary environment variable for apple sillicon processors
                os.environ['DOCKER_DEFAULT_PLATFORM'] = "linux/amd64"
            if "cv_image" not in images:
                os.system("docker build -t cv_image .")
            if "cv_container" not in containers:
                os.system(f"docker run --gpus all -d -t --name cv_container -v {output_directory}:/home/data cv_image")
            if "cv_image" in images and "cv_container" in containers:
                print("Cardiovision is installed successfully")
            else:
                print("Something went wrong, plase try again...")
            return "successfull"
            root_logger.debug("Cardiovision is installed")
        except Exception as e:
            root_logger.error(e)
            raise


class CNN:
    @staticmethod
    def GetCNNComponents():
        """ Returns the CNN saved feartures from the CNN checkpoints folder (weights)
        """
        weights = os.listdir(working_dir / "cnn" / "checkpoints")
        components = [i.split(".")[:-1][0] for i in weights]
        return components


class Docker:
    @staticmethod
    def containers():
        """ Returns the docker containers already installed on the machine
        """
        result = os.popen("docker ps -a").readlines()
        containers = []
        for l in result[1:]:
            line = l.strip("\n")
            containers.append(line.split()[-1])
        return containers

    @staticmethod
    def images():
        """ Returns the docker images already installed on the machine
        """
        result = os.popen("docker image ls").readlines()
        images = []
        for l in result[1:]:
            line = l.strip("\n")
            images.append(line.split()[0])
        images = images[:-1]
        return images


if __name__ == "__main__":
    print(CNN.GetCNNComponents())
    print(platform.platform())
