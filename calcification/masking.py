# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 15:58:26 2022

@author: rz445
"""

import numpy as np
import math
import SimpleITK as sitk
from scipy.ndimage import binary_fill_holes
from skimage.measure import perimeter
from skimage.morphology import binary_closing, disk
from geometry_tools import create_stl



def make_aortic_root_mask(valve,mask_arr,*argv):
    
    """Creates a mask that determines which calcifications should be adjusted.
    The mask roughly corresponds to the area between the cirtual aortic annulus
    and the sinotubular junction that is directly superior and inferior to the 
    valve.
    
    :param valve: valve
    :type valve: 3D NumPy
    :type mask_arr: Binary aortic mask
    :param mask_arr: 3D NumPy
 
    :param arg0: desired directory of nrrd mask
    :type arg0: string
    :param arg1: desired directory of stl mask
    :type arg1: string
    :param arg2: sitk of aorta
    :type arg2: sitk image

    
    :return aortic_root_mask: 3D array of the leaflet adjusted to match the .nrrd file
    :rtype aortic_root_mask: 3D NumPy array
    
    """
    
    #We want to have a mask that includes areas directly above and below the valve
    # within the regions between the virtual aortic annulus (VAA) and sinotubular junction (SJ)
    
    if len(argv)>0 and len(argv)!=3: 
        raise ValueError("This function takes one or four arguments")
    
    #First we flatten the valve to create a 2D image.
    valve_flattened=np.sum(valve,axis=0)
    valve_flattened[valve_flattened >= 1] = 1
    valve_flattened=binary_fill_holes(valve_flattened).astype(int)
    disk_size=int(math.sqrt(math.sqrt(np.shape(valve_flattened)[0]*np.shape(valve_flattened)[1]))) #Rough disk size avoids user specification
    valve_flattened = binary_closing(valve_flattened, disk(disk_size))
    
    #The geometry of this mask is what we need, but we need to translate this into 3D.
    #Find the z coordinates upper and lower coordinates of the valve
    upper_valve_z = np.where(valve)[0].max() #Upper valve z coordinate
    lower_valve_z = np.where(valve)[0].min() #Lower valve z coordinate
    
    #To determine the anatomical virtual aortic annulus we will differentiate 
    #the perimeters of each slice of the scan below the upper valve (SJJ)
    #The minimum gradient indicates the curvature approaching the neck of the 
    #VAA. This will serve as the most inferior bound of the mask
    perimeters=[]
    for z_stack in range(np.shape(valve)[0]):
        if z_stack>lower_valve_z: #if stack is above the most inferior point of valve
            perimeters=np.append(perimeters,np.nan)
        else:
            perimeters=np.append(perimeters,perimeter(mask_arr[z_stack,:,:], neighbourhood=4)) 
    perimeters_diff=np.gradient(perimeters)
    VAA_z = np.nanargmin(perimeters_diff) #Z coordinate of VAA
    mask_depth=upper_valve_z-VAA_z #Mask depth
    #We will make the mask 3D to the depth of SJ and VAA gap
    aortic_root_mask = np.repeat(valve_flattened[np.newaxis,:, :], mask_depth, axis=0)
    #We now need to add the lower and upper buffer to center it in the image
    
    #Lower buffer
    x_lower_buffer = np.zeros((VAA_z,np.shape(valve)[1],np.shape(valve)[2]))
    #Append lower buffer
    aortic_root_mask=np.vstack((x_lower_buffer,aortic_root_mask))
    #Upper buffer
    x_upper_buffer = np.zeros((np.shape(valve)[0]-upper_valve_z,np.shape(valve)[1],np.shape(valve)[2]))
    #Append upper buffer
    aortic_root_mask=np.vstack((aortic_root_mask,x_upper_buffer))
    
    #Convert to boolean for mask operations
    aortic_root_mask=np.array(aortic_root_mask,dtype=bool)
    
    mask_arr_filled=np.zeros(np.shape(mask_arr))
    for z_stack in range(np.shape(mask_arr)[0]):
        mask_arr_filled[z_stack,:,:] = binary_closing(
                        mask_arr[z_stack,:,:], disk(disk_size))
        
        
    mask_arr_filled=np.array(mask_arr_filled,dtype=bool)
    
    #Clip mask with the mask of the aorta for aesthetics
    aortic_root_mask=np.logical_and(aortic_root_mask,mask_arr_filled)
    
    if len(argv)==3: #Options to save the .nrrd and .STL
        aortic_root_mask_path_nrrd = argv[0]
        aortic_root_mask_path_stl = argv[1]
        raw = argv[2]
        aortic_root_mask=np.array(aortic_root_mask,dtype=int)        
        
        aortic_root_mask_info = sitk.GetImageFromArray(aortic_root_mask) #Convert image to sitk recognized image
        aortic_root_mask_info.CopyInformation(raw) #Copy image data info from original nrrd
        sitk.WriteImage(aortic_root_mask_info,aortic_root_mask_path_nrrd) #Write .nrrd image
        create_stl(aortic_root_mask_path_nrrd,aortic_root_mask_path_stl) #create stl of processed image
    
    aortic_root_mask=np.array(aortic_root_mask,dtype=bool)   

    return aortic_root_mask