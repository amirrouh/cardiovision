import sys
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from utils.io import FileFolders
from utils.config import input_file
from calcification.src.calcification_detection import detect_and_move_calcs

predicted_path = str(FileFolders.files['cnn']['predicted_label'])
image_path = input_file

valve_path_1 = str(FileFolders.files['valve']['L_cusp'])
valve_path_2 = str(FileFolders.files['valve']['R_cusp'])
valve_path_3 = str(FileFolders.files['valve']['N_cusp'])

valve_path_1_stl = str(FileFolders.files['valve']['L_cusp_stl'])
valve_path_2_stl = str(FileFolders.files['valve']['R_cusp_stl'])
valve_path_3_stl = str(FileFolders.files['valve']['N_cusp_stl'])

aortic_root_mask_path_nrrd = str(FileFolders.files['calcification']['aortic_root_mask_path_nrrd'])
aortic_root_mask_path_stl = str(FileFolders.files['calcification']['aortic_root_mask_path_stl'])

calcs_path_nrrd=str(FileFolders.files['calcification']['calcs_path_nrrd'])
calcs_path_stl=str(FileFolders.files['calcification']['calcs_path_stl'])
calcs_path_nrrd_corr=str(FileFolders.files['calcification']['calcs_path_nrrd_corr'])
calcs_path_stl_corr=str(FileFolders.files['calcification']['calcs_path_stl_corr'])



detect_and_move_calcs(image_path,predicted_path,valve_path_1,valve_path_2,valve_path_3,\
                          calcs_path_nrrd,calcs_path_stl,calcs_path_nrrd_corr,calcs_path_stl_corr,\
                              aortic_root_mask_path_nrrd,aortic_root_mask_path_stl)
    