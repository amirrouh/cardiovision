import sys
import os
import distutils.log
import distutils.dir_util
import pandas as pd

this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = os.path.join(this_directory, '..', '..')
sys.path.append(working_dir)

from analysis.src.core import split, get_ply_volume
from config import output_dir
from utils.io import FileFolders
from config import verbose

split(FileFolders.folders['global']['shared'])

cusps = ['left', 'right', 'non', 'total']

volumes = {}
for c in cusps[:-1]:
    if verbose:
        print(f"Calcium districution is being calculated for {c}")
    
    calc_ply_file = FileFolders.files['analysis'][f"{c}_cusp"]
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

df.to_csv(FileFolders.files['analysis']['calcium_volumes'])
