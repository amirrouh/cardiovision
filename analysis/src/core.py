import sys
import os
from pathlib import Path
import numpy as np

import pandas as pd

this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = os.path.join(this_directory, '..', '..')
sys.path.append(working_dir)

from analysis.src.helpers import create_folders, split, get_ply_volume
from config import output_dir, verbose

create_folders()

# split(output_dir)

cusps = ['left', 'right', 'non', 'total']

result_files = list(map(str, Path(output_dir).rglob("*")))

volumes = {}
for c in cusps:
    if verbose:
        print(f"Calcium districution is being calculated for {c}")
    
    calc_ply_file = os.path.join(output_dir, f"calcium_{c}.ply")
    if os.path.isfile(calc_ply_file):
        volumes[c] = get_ply_volume(calc_ply_file)
    else:
        volumes[c] = 0
    # calculate total calcium burden

values = (list(volumes.values()))
volumes['total'] = sum(values)
        
if volumes:
    df = pd.DataFrame(list(volumes.values()), index=cusps, columns=['volume (mm^3)'])
    df.index.name = 'cusp'
else:
    print("No volumes calculated.")

if verbose:
    print(df)

df.to_csv(os.path.join(output_dir, 'calcium_volumes.csv'))