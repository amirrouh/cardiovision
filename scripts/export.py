import sys
import os
from pathlib import Path
import shutil
from time import sleep

sys.path.append(os.getcwd())
import ui.config as config


SECRET_KEY = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)

if SECRET_KEY:
    # running in a Docker container

    output_directory_path = Path("/home/data/cardiovision_results/")

    geometries_dir = output_directory_path / 'geometries'
    geometries_dir.mkdir(parents=True, exist_ok=True)

    weights_dir = output_directory_path / 'weights'
    weights_dir.mkdir(parents=True, exist_ok=True)

    all_dir = output_directory_path / 'all'
    all_dir.mkdir(parents=True, exist_ok=True)


    weights_path = Path("/home/app/cnn/intermediate/models/set_1_unet2d/")
    weights = weights_path.rglob("*.hdf5")
    latest_weight = max([f for f in weights], key=lambda item: item.stat().st_ctime)


    shutil.copy2(latest_weight, str(output_directory_path / 'weights' / f"{config.component}.hdf5"))

else:
    # If running outside of the container
    os.system(f"docker exec -ti cv_container python /home/app/scripts/export.py")
    os.system(f"docker cp cv_container:/home/data/cardiovision_results/. {config.output_directory}")

