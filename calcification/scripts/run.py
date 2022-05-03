import sys
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from utils.io import FileFolders
from utils.settings import input_file
from calcification.src.calcification_detection import detect_and_move_calcs

predicted_path = FileFolders.files['cnn']['predicted_label']
image_path = input_file

valve_path_1 = FileFolders.files['valve']['L_cusp']
valve_path_2 = FileFolders.files['valve']['R_cusp']
valve_path_3 = FileFolders.files['valve']['N_cusp']

valve_path_1_stl = FileFolders.files['valve']['L_cusp_stl']
valve_path_2_stl = FileFolders.files['valve']['R_cusp_stl']
valve_path_3_stl = FileFolders.files['valve']['N_cusp_stl']

aortic_root_mask_path_nrrd = FileFolders.files['calcification']['aortic_root_mask_path_nrrd']
aortic_root_mask_path_stl = FileFolders.files['calcification']['aortic_root_mask_path_stl']

calcs_path_nrrd="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\calcs.nrrd"
calcs_path_stl="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\calcs.stl"
calcs_path_nrrd_corr="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\calcs_corr.nrrd"
calcs_path_stl_corr="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\calcs_corr.stl"

aortic_root_mask_path_nrrd="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\mask.nrrd"
aortic_root_mask_path_stl="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\mask.stl"


detect_and_move_calcs(image_path,predicted_path,valve_path_1,valve_path_2,valve_path_3,calcs_path_nrrd,calcs_path_stl,calcs_path_nrrd_corr,calcs_path_stl_corr,aortic_root_mask_path_nrrd,aortic_root_mask_path_stl)

    