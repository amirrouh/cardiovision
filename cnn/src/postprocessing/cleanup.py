import os
import sys
from pathlib import Path

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..', '..'))


from utils.io import FileFolders
folders = FileFolders.folders
cnn_shared = folders['cnn']['shared']
global_shared = folders['global']['shared']

import numpy as np
from skimage import filters
from skimage.morphology import ball
from skimage.measure import label   
from scipy import ndimage
import SimpleITK as sitk
import vtk


def create_stl(nrrd_dir,stl_dir):

    #Read information from nrrd
    reader = vtk.vtkNrrdReader()
    reader.SetFileName(nrrd_dir)
    reader.Update()
    
    #Implements marching cube operation
    dmc = vtk.vtkDiscreteMarchingCubes()
    dmc.SetInputConnection(reader.GetOutputPort())
    dmc.GenerateValues(1, 1, 1)
    dmc.Update()
    
    smoothFilter = vtk.vtkSmoothPolyDataFilter()
    smoothFilter.SetNumberOfIterations(300)
    smoothFilter.SetRelaxationFactor(0.1);
    smoothFilter.FeatureEdgeSmoothingOff();
    smoothFilter.BoundarySmoothingOn();
    smoothFilter.SetInputConnection(dmc.GetOutputPort())
    smoothFilter.Update()
    
    #Write .stl
    writer = vtk.vtkSTLWriter()
    writer.SetInputConnection(smoothFilter.GetOutputPort())
    writer.SetFileTypeToBinary()
    writer.SetFileName(stl_dir)
    writer.Write()

    return


def cleanup_geometry(input_path_nrrd, output_path_nrrd, output_path_STL): 
    
    """ Smoothens and closes small holes and retains only largest island in .nrrd file
    
    Args:
        param1 (str): input path of nrrd (with .nrrd extension)
        param2 (str): cleaned nrrd output path (with .nrrd extension)
        param3 (str): cleanred stl output path (with .stl extension)
    
        
    Returns:
        nrrd file: Located at the output path specified
        stl file: Located at the output path specified
    
    """
    
    #Opens the images
    raw = sitk.ReadImage(str(input_path_nrrd))
    
    # reset the image origin and direction
    raw.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))
    raw.SetOrigin((0, 0, 0))
    
    #Extracts array from image data
    raw_arr = np.array(sitk.GetArrayFromImage(raw))
    
    threshold=0.5 #Threshold value. Anything below will be background
    binary_mask=np.where(raw_arr>threshold, 1, 0) #Convert to binary array
    
    #Remove some of the small holes in the image
    #Scans through slices in 2D on two different axes to remove holes
    for img_slice in range(np.shape(binary_mask)[0]):
        binary_mask[img_slice,:,:]=ndimage.binary_fill_holes(binary_mask[img_slice,:,:])
    for img_slice in range(np.shape(binary_mask)[2]):
        binary_mask[:,:,img_slice]=ndimage.binary_fill_holes(binary_mask[:,:,img_slice])
    
    #Apply a median filter to the image
    img=filters.median(binary_mask,ball(5))
    
    #Make edge layers blank. This enables marching cubes operation in vtk to work
    img[0,:,:]=np.zeros((1,np.shape(binary_mask)[1],np.shape(binary_mask)[2]),dtype=bool) #filled slices
    img[-1,:,:]=np.zeros((1,np.shape(binary_mask)[1],np.shape(binary_mask)[2]),dtype=bool) #filled slices
    img[:,0,:]=np.zeros((1,np.shape(binary_mask)[0],np.shape(binary_mask)[2]),dtype=bool) #filled slices
    img[:,-1,:]=np.zeros((1,np.shape(binary_mask)[0],np.shape(binary_mask)[2]),dtype=bool) #filled slices
    img[:,:,0]=np.zeros((1,np.shape(binary_mask)[0],np.shape(binary_mask)[1]),dtype=bool) #filled slices
    img[:,:,-1]=np.zeros((1,np.shape(binary_mask)[0],np.shape(binary_mask)[1]),dtype=bool) #filled slices

    
    #Process to keep only the largest connected component
    labels = label(img) #All seperated labels
    assert( labels.max() != 0 )
    largest_label = labels == np.argmax(np.bincount(labels.flat)[1:])+1 #Largest label
    img=largest_label.astype(int) #Convert from bool to int
    
    
    img_preprocessed = sitk.GetImageFromArray(img) #Convert image to sitk recognized image
    img_preprocessed.CopyInformation(raw) #Copy image data info from original nrrd
    
    
    sitk.WriteImage(img_preprocessed,output_path_nrrd) #Write .nrrd image
    
    create_stl(output_path_nrrd,output_path_STL) #create stl of processed image
        
    return

input_path_nrrd = cnn_shared / 'predicted.nrrd'
output_path_nrrd = global_shared / 'predicted_smoothed.nrrd'
output_path_STL = global_shared / 'predicted.stl'
cleanup_geometry(str(input_path_nrrd), str(output_path_nrrd), str(output_path_STL))
