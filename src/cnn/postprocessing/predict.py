"""
Predict the outcome nrrd file given the input image
"""
import os.path
import SimpleITK as sitk
import numpy as np

import sys
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..'))

from cnn.helpers.utils import resample, pad_crop
from cnn.helpers.unet import UNet
from cnn.helpers import settings
from cnn.initialization.create_folders import shared_dir


# resample image
sample_img = sitk.ReadImage(str(settings.input_file))

sample_img.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))
sample_img.SetOrigin((0, 0, 0))

inplane_spacing = (sample_img.GetSpacing()[0] + sample_img.GetSpacing()[1])/2
z_spacing_original = sample_img.GetSpacing()[2]
z_size_original = sample_img.GetSize()[2]
sample_img = resample(sample_img, output_spacing=(inplane_spacing, inplane_spacing, z_spacing_original),
               interplator=sitk.sitkLinear)
sample_img = pad_crop(sample_img, output_size=(512, 512, z_size_original))



# convert to array
X = sitk.GetArrayFromImage(sample_img)
X = np.expand_dims(X, axis=-1).astype(np.float32)

# Create CNN model
cnn = UNet(n_classes=settings.n_classes)
model = cnn.model()

# local CNN model
model.load_weights(settings.model_checkpoint)

# prediction
pred_nda = model.predict(X, batch_size=64, verbose=False)

# keep class 1 (out of 0, 1 classes where 0 is background and 1 is foreground)
pred_tmp = pred_nda[..., 1]
pred_image = sitk.GetImageFromArray(pred_tmp)
pred_image.CopyInformation(sample_img)

sitk.WriteImage(pred_image, os.path.join(shared_dir, 'predicted.nrrd'), True)

