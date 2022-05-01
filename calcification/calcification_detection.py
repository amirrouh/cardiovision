# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 14:36:39 2022

@author: rz445
"""
# %matplotlib auto
#%matplotlib inline
import numpy as np
import SimpleITK as sitk
from scipy.ndimage import zoom,center_of_mass,label
from geometry_tools import create_stl, ply_to_leaflet
from masking import make_aortic_root_mask
       
def detect_and_move_calcs(raw_path,mask_path,valve_path_1,valve_path_2,valve_path_3,\
                          calcs_path_nrrd,calcs_path_stl,*argv):
    
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
    
    argv*
    :param arg[0]: .nrrd directory for corrected calcifications
    :type arg[0]: string
    :param arg[1]: .stl directory for corrected calcifications
    :type arg[1]: string
    :param arg[2]: .nrrd directory for aortic root mask
    :type arg[2]: string
    :param arg[3]: .stl directory for aortic root mask
    :type arg[3]: string

    """
    if len(argv)>0 and len(argv)!=4: 
        raise ValueError("Either 7 or 11 arguments are needed")
    
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
    
    if len(argv)==4: #Options to save the .nrrd and .STL
    
        calcs_corrected=np.zeros(np.shape(calcs))
        blank_arr=np.zeros(np.shape(calcs))
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
                #Distance in Z direction between calc COM and valve
                distance=int(valve_z_idx-com_z_idx)
                #Append calcification
                calcs_corrected=calcs_corrected+np.roll(calc_org,distance,axis=0)
                    
        #Create stl and nrrd of corrected calcs
        calcs_info_corr = sitk.GetImageFromArray(calcs_corrected) #Convert image to sitk recognized image
        calcs_info_corr.CopyInformation(raw) #Copy image data info from original nrrd
        sitk.WriteImage(calcs_info_corr,calcs_path_nrrd_corr) #Write .nrrd image
        create_stl(calcs_path_nrrd_corr,calcs_path_stl_corr) #create stl of processed image
    
    return

mask_path="C:\\Users\\RZ445\\Downloads\\mask0.nrrd"
raw_path="C:\\Users\\RZ445\\Downloads\\ct0.nrrd"

valve_path_1="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\L_complete_cusp.ply"
valve_path_2="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\R_complete_cusp.ply"
valve_path_3="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\NC_complete_cusp.ply"

valve_path_1_stl="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\L_complete_cusp.stl"
valve_path_2_stl="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\R_complete_cusp.stl"
valve_path_3_stl="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\NC_complete_cusp.stl"

aortic_root_mask_path_nrrd="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\mask.nrrd"
aortic_root_mask_path_stl="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\mask.stl"

calcs_path_nrrd="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\calcs.nrrd"
calcs_path_stl="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\calcs.stl"
calcs_path_nrrd_corr="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\calcs_corr.nrrd"
calcs_path_stl_corr="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\calcs_corr.stl"

aortic_root_mask_path_nrrd="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\mask.nrrd"
aortic_root_mask_path_stl="C:\\Users\\RZ445\\Downloads\\temp\\valve_cusps\\mask.stl"

detect_and_move_calcs(raw_path,mask_path,valve_path_1,valve_path_2,valve_path_3,calcs_path_nrrd,calcs_path_stl,calcs_path_nrrd_corr,calcs_path_stl_corr,aortic_root_mask_path_nrrd,aortic_root_mask_path_stl)
# detect_and_move_calcs(raw_path,mask_path,valve_path_1,valve_path_2,valve_path_3,calcs_path_nrrd,calcs_path_stl)

    


