import random
import numpy as np
import SimpleITK as sitk
from skimage.util import random_noise
from skimage.transform import resize

class AugmentImage():
    def __init__(self) -> None:
        pass
    def define_reference(size, spacing, origin, direction, pixelID):
        reference = sitk.Image(size, pixelID)
        reference.SetSpacing(spacing)
        reference.SetOrigin(origin)
        reference.SetDirection(direction)
        return reference, GetMetaData(reference)
    def transform_image(image, angles, offset, fill_value, size=[], spacing=[], origin=None, direction = []):
        meta = GetMetaData(image)
        center = GetCenter(image)
        if not size:
            size = meta['size']
        if not spacing:
            spacing = meta['spacing']
        if origin==None:
            origin = meta['origin']
        if not direction:
            direction = meta['direction']
        reference, reference_meta = AugmentImage.define_reference(size, spacing, origin, direction, meta['pixelID'])
        rotation_center = GetCenter(reference)

        # align reference image origin to image origin
        T0 = sitk.AffineTransform(reference_meta['dimension'])
        T0.SetMatrix(np.identity(reference_meta['dimension']).flatten())
        T0.SetTranslation(np.array(meta['origin']) - reference_meta['origin'])

        # Modify the transformation to align the centers of the original and reference image instead of their origins.
        T1 = sitk.TranslationTransform(reference_meta['dimension'])
        T1.SetOffset(np.array(T0.GetInverse().TransformPoint(center) - rotation_center))

        T_temp = sitk.CompositeTransform([T0, T1])
        resample_center = T_temp.GetInverse().TransformPoint(center - offset)
        # transformation parameters
        T_param = similarity3D_parameter_space_regular_sampling(angles[0], angles[1], angles[2], 
                                                                resample_center[0]-rotation_center[0], 
                                                                resample_center[1]-rotation_center[1], 
                                                                resample_center[2]-rotation_center[2], 1)[0]
        # Set the augmenting transform's center so that rotation is around the image center.
        T2 = sitk.Similarity3DTransform()
        T2.SetCenter(rotation_center)
        T2.SetParameters(T_param)

        T = sitk.CompositeTransform([T0, T1, T2])

        return sitk.Resample(image, reference, T, sitk.sitkLinear, fill_value, )
    def add_noise_gaussian(img):   
        rows, cols, ch = sitk.GetArrayFromImage(img).shape
        val = np.random.uniform(0.0005, 0.005)

        # Full resolution
        # noise_im1 = np.zeros((rows//2, cols//2, ch//2))
        # noise_im1 = random_noise(noise_im1, mode='gaussian', var=(val*2)**2, clip=False)
        # noise_im1 = resize(noise_im1, (rows, cols, ch))

        # # Half resolution
        # noise_im2 = np.zeros((rows//4, cols//4, ch//4))
        # noise_im2 = random_noise(noise_im2, mode='gaussian', var=(val*4)**2, clip=False)  # Use val*2 (needs tuning...)
        # noise_im2 = resize(noise_im2, (rows, cols, ch))  # Upscale to original image size

        # # Quarter resolution
        # noise_im3 = np.zeros((rows//8, cols//8, ch//8))
        # noise_im3 = random_noise(noise_im3, mode='gaussian', var=(val*8)**2, clip=False)  # Use val*4 (needs tuning...)
        # noise_im3 = resize(noise_im3, (rows, cols, ch))  # What is the interpolation method?

        # noise_im = noise_im1 + noise_im2 + noise_im3  # Sum the noise in multiple resolutions (the mean of noise_im is around zero).

        noise_im = np.zeros((rows, cols, ch))
        noise_im = random_noise(noise_im, mode='gaussian', var=(val)**2, clip=False)
        
        return  ArrayToImage(sitk.GetArrayFromImage(img) + noise_im, img)
    def augment_image(image, angles_range, offset_range, mask = [], nr_duplicates=1, fill_value=0, size=[], spacing=[], origin=None, direction = [], seed=0):
        augmented_images = []
        if type(mask) != list:
            augmented_masks = []
        for i in range(nr_duplicates):
            random.seed(seed+i)
            np.random.seed(seed+i)
            angle1 = random.uniform(angles_range[0][0], angles_range[0][1])
            angle2 = random.uniform(angles_range[1][0], angles_range[1][1])
            angle3 = random.uniform(angles_range[2][0], angles_range[2][1])
            offset_x = random.uniform(offset_range[0][0], offset_range[0][1])
            offset_y = random.uniform(offset_range[1][0], offset_range[1][1])
            offset_z = random.uniform(offset_range[2][0], offset_range[2][1])
            #augmented_images.append(AugmentImage.add_noise_gaussian(
            #    AugmentImage.transform_image(image, 
            #                                 [angle1, angle2, angle3], 
            #                                 [offset_x, offset_y, offset_z], 
            #                                 int(fill_value), 
            #                                 size, spacing, origin, direction)))
            augmented_images.append(AugmentImage.transform_image(image, 
                                             [angle1, angle2, angle3], 
                                             [offset_x, offset_y, offset_z], 
                                             int(fill_value), 
                                             size, spacing, origin, direction))
            if type(mask) != list:
                augmented_masks.append(AugmentImage.transform_image(mask, [angle1, angle2, angle3], [offset_x, offset_y, offset_z], 0, size, spacing, origin, direction))
        if type(mask) != list:
            return (augmented_images, augmented_masks)
        else:
            return augmented_images

def GetMetaData(img):
    meta = {}
    meta['dimension'] = img.GetDimension()
    meta['size'] = img.GetSize()
    meta['spacing'] = img.GetSpacing()
    meta['direction'] = img.GetDirection()
    meta['origin'] = img.GetOrigin()
    meta['pixelID'] = img.GetPixelIDValue()
    return meta
def GetCenter(img):
    # caculate reference center
    return np.array(img.TransformContinuousIndexToPhysicalPoint(np.array(img.GetSize()) / 2.0))
def ArrayToImage(arr, ref_img):
    img = sitk.GetImageFromArray(arr)
    img.SetDirection(ref_img.GetDirection())
    img.SetOrigin(ref_img.GetOrigin())
    img.SetSpacing(ref_img.GetSpacing())
    return img
def similarity3D_parameter_space_regular_sampling(
    thetaX, thetaY, thetaZ, tx, ty, tz, scale
):
    """
    Create a list representing a regular sampling of the 3D similarity transformation parameter space. As the
    SimpleITK rotation parameterization uses the vector portion of a versor we don't have an
    intuitive way of specifying rotations. We therefor use the ZYX Euler angle parametrization and convert to
    versor.
    Args:
        thetaX, thetaY, thetaZ: numpy ndarrays with the Euler angle values to use.
        tx, ty, tz: numpy ndarrays with the translation values to use.
        scale: numpy array with the scale values to use.
    Return:
        List of lists representing the parameter space sampling (vx,vy,vz,tx,ty,tz,s).
    """
    return [
        list(eul2quat(parameter_values[0], parameter_values[1], parameter_values[2]))
        + [np.ndarray.item(p) for p in parameter_values[3:]]
        for parameter_values in np.nditer(
            np.meshgrid(thetaX, thetaY, thetaZ, tx, ty, tz, scale)
        )
    ]
def eul2quat(ax, ay, az, atol=1e-8):
    """
    Translate between Euler angle (ZYX) order and quaternion representation of a rotation.
    Args:
        ax: X rotation angle in radians.
        ay: Y rotation angle in radians.
        az: Z rotation angle in radians.
        atol: tolerance used for stable quaternion computation (qs==0 within this tolerance).
    Return:
        Numpy array with three entries representing the vectorial component of the quaternion.

    """
    # Create rotation matrix using ZYX Euler angles and then compute quaternion using entries.
    cx = np.cos(ax)
    cy = np.cos(ay)
    cz = np.cos(az)
    sx = np.sin(ax)
    sy = np.sin(ay)
    sz = np.sin(az)
    r = np.zeros((3, 3))
    r[0, 0] = cz * cy
    r[0, 1] = cz * sy * sx - sz * cx
    r[0, 2] = cz * sy * cx + sz * sx

    r[1, 0] = sz * cy
    r[1, 1] = sz * sy * sx + cz * cx
    r[1, 2] = sz * sy * cx - cz * sx

    r[2, 0] = -sy
    r[2, 1] = cy * sx
    r[2, 2] = cy * cx

    # Compute quaternion:
    qs = 0.5 * np.sqrt(r[0, 0] + r[1, 1] + r[2, 2] + 1)
    qv = np.zeros(3)
    # If the scalar component of the quaternion is close to zero, we
    # compute the vector part using a numerically stable approach
    if np.isclose(qs, 0.0, atol):
        i = np.argmax([r[0, 0], r[1, 1], r[2, 2]])
        j = (i + 1) % 3
        k = (j + 1) % 3
        w = np.sqrt(r[i, i] - r[j, j] - r[k, k] + 1)
        qv[i] = 0.5 * w
        qv[j] = (r[i, j] + r[j, i]) / (2 * w)
        qv[k] = (r[i, k] + r[k, i]) / (2 * w)
    else:
        denom = 4 * qs
        qv[0] = (r[2, 1] - r[1, 2]) / denom
        qv[1] = (r[0, 2] - r[2, 0]) / denom
        qv[2] = (r[1, 0] - r[0, 1]) / denom
    return qv
def GetSliceCenter(slice):
    label_statistic = sitk.LabelIntensityStatisticsImageFilter()
    label_statistic.Execute(slice, slice == 1)
    center_idx= slice.TransformPhysicalPointToIndex(label_statistic.GetCenterOfGravity(1))
    return center_idx[:2]
def GetCenterline(mask):
    center_pt = np.zeros((mask.GetDimension(), mask.GetDepth()))
    center_idx = np.zeros(center_pt.shape)
    empty_idx = []
    for i in range(0, mask.GetDepth()):
        slice_arr = sitk.GetArrayFromImage(mask[:,:,i])
        if slice_arr[slice_arr==1].size > 10:
            center_idx[:2,i] = GetSliceCenter(mask[:,:,i])
            center_idx[2,i] = i
            center_pt[:,i] = mask.TransformContinuousIndexToPhysicalPoint(list(center_idx[:,i]))
        else:
            empty_idx.append(i)
    center_pt = np.delete(center_pt, empty_idx, axis=1)
    return center_pt, empty_idx