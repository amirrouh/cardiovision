#!/bin/bash

case $1 in
    # -p -i -t should be run from docker
    -p) # predicting
    eval "$(conda shell.bash hook)"
    conda activate cardiovision
    python scripts/generate_settings.py $2 $3
    python scripts/run.py
    ;;
    -i) # initialization (resampling and data generation)
    eval "$(conda shell.bash hook)"
    conda activate training
    python scripts/generate_settings.py -new
    python cnn/src/preprocess/1_resample.py
    python cnn/src/preprocess/2_split.py
    python cnn/src/preprocess/3_datagen.py
    ;;
    -t)
    eval "$(conda shell.bash hook)"
    conda activate cnn
    python scripts/generate_settings.py -new
    python cnn/src/train/1_train.py
    ;;
    -e)
    eval "$(conda shell.bash hook)"
    conda activate cnn
    python scripts/io.py -new
    python cnn/src/train/1_train.py
    ;;
    *)
    echo "please use option '-p' for predictions "
esac
