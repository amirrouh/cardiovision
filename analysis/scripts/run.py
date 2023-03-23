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

split(FileFolders.files['analysis']['analysis_shared'])

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

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))


distutils.log.set_verbosity(distutils.log.DEBUG)
distutils.dir_util.copy_tree(
    FileFolders.folders['analysis']['shared'],
    output_dir,
    update=1,
    verbose=0,
)
