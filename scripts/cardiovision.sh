#!/bin/bash

case $1 in
    -p) # predicting
    eval "$(conda shell.bash hook)"
    conda activate cardiovision
    python scripts/generate_settings.py $2
    python scripts/run.py
    ;;
    *)
    echo "please use option '-p' for predictions "
esac