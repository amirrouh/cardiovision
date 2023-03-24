import sys
import os

import numpy as np
import SimpleITK as sitk
from scipy.ndimage import zoom,center_of_mass,label

this_directory = os.path.abspath(os.path.dirname(__file__))
working_dir = os.path.join(this_directory, '..')
sys.path.append(working_dir)

from utils.io import FileFolders

from calcification.src.geometry_tools import create_stl, ply_to_leaflet
from calcification.src.masking import make_aortic_root_mask


input_file = "/home/data/input_file.nrrd"

       
def detect_and_move_calcs(raw_path,mask_path,valve_path_1,valve_path_2,valve_path_3,\
                          calcs_path_nrrd,calcs_path_stl,calcs_path_nrrd_corr,calcs_path_stl_corr,\
                              aortic_root_mask_path_nrrd,aortic_root_mask_path_stl):
    
    """Creates .nrrd and .stl of calcifications and performs an optional operation
    to correct the positioning of the calcifications so that the center of mass of
    each calcification is within the valve. The calcifications are only adjusted
    in the transverse plane.
    
    :param raw_path: .nrrd raw path directory
    :type raw_path: string
    :param mask_path: .nrrd mask path directory
    :type mask_path: string
    :param valve_path_1: .ply directory for one of three valves
    :type valve_path_1: string
    :param valve_path_2: .ply directory for one of three valves
    :type valve_path_2: string
    :param valve_path_3: .ply directory for one of three valves
    :type valve_path_3: string
    :param calcs_path_nrrd: .nrrd directory for unadjusted calcifications
    :type calcs_path_nrrd: string
    :param calcs_path_stl: .stl directory for unadjusted calcifications
    :type calcs_path_stl: string
    
    :param calcs_path_nrrd_corr: .nrrd directory for corrected calcifications
    :type calcs_path_nrrd_corr: string
    :param calcs_path_stl_corr: .stl directory for corrected calcifications
    :type calcs_path_stl_corr: string
    :param aortic_root_mask_path_nrrd: .nrrd directory for aortic root mask
    :type aortic_root_mask_path_nrrd: string
    :param aortic_root_mask_path_stl: .stl directory for aortic root mask
    :type aortic_root_mask_path_stl: string

    """  
    
    
    calc_thresh=500 #Lower threshold for calcificiation
    multi_factor=10 #Factpr used to interpolate .ply and .nrrd
    
    raw = sitk.ReadImage(str(raw_path)) #Load grayscale image
    raw.SetOrigin((0, 0, 0)) #Set origin
    raw.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1)) #Set direction
    raw_arr = np.array(sitk.GetArrayFromImage(raw))
    raw_spacing=raw.GetSpacing()
    
    mask = sitk.ReadImage(str(mask_path)) #Load binary aorta mask
    mask.SetOrigin((0, 0, 0))
    mask.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))
    mask_arr = np.array(sitk.GetArrayFromImage(mask))
    mask_arr=np.asarray(mask_arr,dtype=bool)
    
    raw_arr_adj=np.copy(raw_arr)
    raw_arr_adj= zoom(raw_arr_adj, (multi_factor*raw_spacing[2], multi_factor*raw_spacing[0], multi_factor*raw_spacing[1])) #change 10 to 1
    raw_arr_adj=np.swapaxes(raw_arr_adj, 0, 2)
    
    #Apply mask onto raw image to remove background
    masked = np.copy(raw_arr)
    masked[~mask_arr] = 0
    
    #Convert .ply leaflets ro NumPy array with correct dimensions and scale
    valve_leaflet_1=ply_to_leaflet(valve_path_1,0.7,1,multi_factor,raw_arr_adj) 
    valve_leaflet_2=ply_to_leaflet(valve_path_2,0.7,1,multi_factor,raw_arr_adj)
    valve_leaflet_3=ply_to_leaflet(valve_path_3,0.7,1,multi_factor,raw_arr_adj)
    
    valve=valve_leaflet_1|valve_leaflet_2|valve_leaflet_3 #Combine valves
    
    #Swap axis and interpolate image to match raw_arr_adj
    valve=np.swapaxes(valve, 0, 2) #Swap axis
    valve= zoom(valve, (1/(multi_factor*raw_spacing[2]), 1/(multi_factor*raw_spacing[0]), 1/(multi_factor*raw_spacing[1]))) #Interpoalte
    
    #Make mask that is used to move certain calcifications
    valve_mask=make_aortic_root_mask(valve,mask_arr,aortic_root_mask_path_nrrd,aortic_root_mask_path_stl,raw)
    
    #Apply mask onto raw image to remove background
    valve_masked = np.copy(raw_arr)
    valve_masked[~valve_mask] = 0
    
    calcs=np.where(masked>calc_thresh, 1, 0) #Isolate calcifications in entire aorta
    calc_labels,cal_num=label(calcs) #Label every calcification detected
    
    #Create stl and nrrd of original calcs
    calcs_info = sitk.GetImageFromArray(calcs) #Convert image to sitk recognized image
    calcs_info.CopyInformation(raw) #Copy image data info from original nrrd
    sitk.WriteImage(calcs_info,calcs_path_nrrd) #Write .nrrd image
    create_stl(calcs_path_nrrd,calcs_path_stl) #create stl of processed image
    
    
    calcs_corrected=np.zeros(np.shape(calcs))
    blank_arr=np.zeros(np.shape(calcs))
    calc_valve=np.zeros(np.shape(calcs))
    
    for calc_label in range(1,cal_num): #Important not to do background of zero
        
        calc_org = np.where(calc_labels == calc_label, 1, 0) #Calcification isolated
        #Centre of Mass (COM) of calcification
        com_idx=center_of_mass(calc_org) 
        com=np.copy(blank_arr)
        #Single element added to blank array which represents COM
        com[round(com_idx[0]),round(com_idx[1]),round(com_idx[2])]=1
    
        #Determine if COM of calc is inside mask
        com_status=np.max(np.logical_and(com,valve_mask)) 
        
        if com_status==False: #When calcification COM is outside of the mask
            #Append unedited calcification. This one does not need to be altered
            calcs_corrected=calcs_corrected+calc_org
        else: #When calcification COM is inside of the mask
            #COM z coordinate
            com_z_idx=int(np.where(com[:,int(round(com_idx[1])),int(round(com_idx[2]))]==1)[0])
            #Average z coordinate of valve directly above/below COM of calcification
            valve_z_idx=int(round(np.mean(np.where(valve[:,int(round(com_idx[1])),int(round(com_idx[2]))]==1))))



            valve_z_idx_array = np.where(valve[:,int(round(com_idx[1])),int(round(com_idx[2]))]==1)
            if len(valve_z_idx_array) > 0:

                valve_z_idx_array = np.array(valve_z_idx_array)
                valve_z_idx_array = valve_z_idx_array[~np.isnan(valve_z_idx_array)] # remove NaN values
                valve_z_idx = int(round(np.mean(valve_z_idx_array)))

                valve_z_idx = int(round(np.nanmean(valve_z_idx_array)))
            else:
                valve_z_idx = 0



            #Distance in Z direction between calc COM and valve
            distance=int(valve_z_idx-com_z_idx)
            #Append calcification
            calcs_corrected=calcs_corrected+np.roll(calc_org,distance,axis=0)
            
            #calc_valve only contains calcium attached to valve
            calc_valve=calc_valve+np.roll(calc_org,distance,axis=0)

                
#    #Create stl and nrrd of corrected calcs
#    calcs_info_corr = sitk.GetImageFromArray(calcs_corrected) #Convert image to sitk recognized image
#    calcs_info_corr.CopyInformation(raw) #Copy image data info from original nrrd
#    sitk.WriteImage(calcs_info_corr,calcs_path_nrrd_corr) #Write .nrrd image
#    create_stl(calcs_path_nrrd_corr,calcs_path_stl_corr) #create stl of processed image
    
    #Creates stl and nrrd of calcs that are touching the valve
    calcs_info_corr = sitk.GetImageFromArray(calc_valve) #Convert image to sitk recognized image
    calcs_info_corr.CopyInformation(raw) #Copy image data info from original nrrd
    sitk.WriteImage(calcs_info_corr,calcs_path_nrrd_corr) #Write .nrrd image
    create_stl(calcs_path_nrrd_corr,calcs_path_stl_corr) #create stl of processed image
    
    
    return