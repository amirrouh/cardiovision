#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate cardiovision
python scripts/run.py
