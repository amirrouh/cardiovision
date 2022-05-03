from doctest import OutputChecker
import os
import pathlib
import sys
from dataclasses import dataclass
from pathlib import Path
import pickle
import shutil

this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = Path(os.path.join(this_directory, '..'))
sys.path.append(working_dir)

from utils import settings


@dataclass
class FileFolders:
    folders = {
        'global': {
            'shared': working_dir / 'shared',
            'valve_cusps': working_dir / 'shared' / 'valve_cusps',
            'output_dir': Path(settings.output_dir)
        },
    
        'cnn': {
            'intermediate': working_dir / 'cnn' / 'intermediate',
            'data': working_dir / 'cnn' / 'intermediate' / 'data',
            'sheets': working_dir / 'cnn' / 'intermediate' / 'data' / 'sheets',
            'images': working_dir / 'cnn' / 'intermediate' / 'data' / 'images',
            'arrays': working_dir / 'cnn' / 'intermediate' / 'data' / 'arrays',
            'models': working_dir / 'cnn' / 'intermediate' / 'models',
            'snaps': working_dir / 'cnn' / 'intermediate' / 'snaps',
            'shared': working_dir / 'cnn' / 'shared',
        },
        
        'landmark': {
            'landmark_shared': working_dir / 'landmark' / 'shared',
            'landmark_temp': working_dir / 'landmark' / 'shared' / 'temp',
        },
        
        'valve': {
            'valve_shared': working_dir / 'valve' / 'shared',
            'shell': working_dir / 'valve' / 'shared' / 'temp' / 'shell',
            'pointcloud': working_dir / 'valve' / 'shared' / 'temp' / 'pointcloud',
            'final': working_dir / 'valve' / 'shared' / 'temp' / 'final',
        },
        'calcification': {
            'calcification_shared': working_dir / 'calcification' / 'shared',
        }
    }
    
    files = {
        'global': {
            
        },
        'cnn': { 
            'aorta_stl': working_dir / 'shared' / 'predicted.stl',
            'predicted_label': working_dir / 'shared' / 'predicted_smoothed.nrrd'
        },
        'landmark': {
            'log_file': working_dir/'landmark'/'shared'/'temp'/'landmark_detection.log',
            'drawings': working_dir/'landmark'/'shared'/'temp'/'drawings.pkl',
            'triangles_info': working_dir/'landmark'/'shared'/'temp'/'triangles_info.pkl',
            'indices': working_dir/'landmark'/'shared'/'temp'/'indices.pkl',
            'image_data': working_dir/'landmark'/'shared'/'temp'/'image_data.pkl',
            'landmarks': working_dir / 'shared'/'landmarks.csv',
            'image_nrrd': working_dir/'landmark'/'shared'/'image.nrrd',
        },
        'valve': {
            'L_cusp': working_dir/'shared'/'valve_cusps'/'L_complete_cusp.ply',
            'R_cusp': working_dir/'shared'/'valve_cusps'/'R_complete_cusp.ply',
            'N_cusp': working_dir/'shared'/'valve_cusps'/'NC_complete_cusp.ply',
            'L_cusp_stl': working_dir/'shared'/'valve_cusps'/'L_complete_cusp_stl.stl',
            'R_cusp_stl': working_dir/'shared'/'valve_cusps'/'R_complete_cusp_stl.stl',
            'N_cusp_stl': working_dir/'shared'/'valve_cusps'/'NC_complete_cusp_stl.stl',

            },
        'calcification': {
            'aortic_root_mask_path_nrrd': working_dir/'calcification'/'shared'/'mask.nrrd',
            'aortic_root_mask_path_stl': working_dir/'calcification'/'shared'/'mask.stl',

            'calcs_path_nrrd':working_dir/'calcification'/'shared'/'calcs.nrrd',
            'calcs_path_stl':working_dir/'calcification'/'shared'/'calcs.stl',
            'calcs_path_nrrd_corr':working_dir/'calcification'/'shared'/'calcs_corr.nrrd',
            'calcs_path_stl_corr':working_dir/'calcification'/'shared'/'calcs_corr.stl',

            'aortic_root_mask_path_nrrd':working_dir/'calcification'/'shared'/'mask.nrrd',
            'aortic_root_mask_path_stl':working_dir/'calcification'/'shared'/'mask.stl',
            },
    }
    

class Functions:
    @staticmethod
    def save_pickle(variable, path):
        with open(path, 'wb') as file:
            pickle.dump(variable, file)

    @staticmethod
    def read_pickle(path):
        with open(path, 'rb') as file:
            data = pickle.load(file)
        return data
    
    @staticmethod
    def get_files_folders(exclude=''):
        folders_dict = FileFolders.folders
        folder_names = folders_dict.keys()
        folders = []
        for i in folder_names:
            if i != exclude:
                for j in folders_dict[i].values():
                    folders.append(j)
        return folders
    

    @staticmethod
    def create():
        folders = Functions.get_files_folders()
        folder_paths = folders
        new_paths = [working_dir/i for i in folder_paths]
        for d in new_paths:
            d.mkdir(parents=True, exist_ok=True)


    @staticmethod
    def clean(exclude:list=False):
        """ Remove the created folders

        Parameters
        ----------
        exclude : list, optional
            the modules to be excluded from cleaninig, by default False
        """
        folders = Functions.get_files_folders()
        folder_paths = folders
        new_paths = [working_dir/i for i in folder_paths]
        for d in new_paths:
            clean = True
            if exclude:
                exclude_str = [str(i) for i in exclude]
                for i in exclude_str:
                    if i in str(d):
                        clean = False
            if clean:    
                try:
                    shutil.rmtree(d, ignore_errors=False)
                except:
                    pass

    @staticmethod
    def refresh(exclude: list = False):
        Functions.clean(exclude)
        Functions.create()

        
    @staticmethod
    def sync(source_dir: pathlib.Path, destination_dir: pathlib.Path):
        """
        One way sync from source dir to destination dir """
        
        
        src_files = list(source_dir.rglob('*'))
        src_files_str_relative = [str(i.relative_to(source_dir)) for i in list(src_files)]
        dst_files = list(destination_dir.rglob('*'))
        dst_files_str_relative = [str(i.relative_to(destination_dir)) for i in list(dst_files)]
           
        # cleanup the destination    
        for f in dst_files:
            dst_rel_path = f.relative_to(destination_dir)
            if str(dst_rel_path) not in src_files_str_relative:
                if f.is_dir:
                    try:
                        shutil.rmtree(f)
                    except:
                        os.remove(str(f))
                else:
                    try:
                        os.remove(str(f))
                    except:
                        shutil.rmtree(f)
                        
        shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
        
def main():
    ff = Functions()
    src = Path('/home/amir/projects/cardiovision/shared')
    dst = Path('/mnt/c/Users/amir/Documents/temp')
    ff.sync(src, dst)
        
if __name__ == "__main__":
    main()
