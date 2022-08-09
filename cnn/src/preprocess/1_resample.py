import os
import sys
from pathlib import Path

import SimpleITK as sitk
import pandas as pd
from tqdm import tqdm

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..', '..'))

from utils.settings import training_dir
from cnn.src.helpers.utils import resample, pad_crop, Parser
from utils.io import FileFolders as ff
from utils.io import Functions


folders = ff.folders

images_folder = folders['cnn']['images']
sheets_folder = folders['cnn']['sheets']

# creating required folders for training
Functions.create()

if __name__ == '__main__':
    image_set = "set_1"
    cts_dir = Path(training_dir)/'images'
    cts = list(cts_dir.glob('*.nrrd'))
    cts.sort()
    lbls_dir = Path(training_dir)/'labels'
    lbls = list(lbls_dir.glob('*.nrrd'))
    lbls.sort()
    output_folder = os.path.join(images_folder, image_set)
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    d = list()

    for i, ct in enumerate(tqdm(cts)):
        img = sitk.ReadImage(str(ct))
        label = sitk.ReadImage(str(lbls[i]))

        inplane_spacing = 0.35
        z_spacing_original = img.GetSpacing()[2]
        z_size_original = img.GetSize()[2]

        img = resample(img, output_spacing=(inplane_spacing, inplane_spacing, z_spacing_original),
                       interplator=sitk.sitkLinear)
        img = pad_crop(img, output_size=(512, 512, z_size_original))
        #
        label = resample(label, output_spacing=(inplane_spacing, inplane_spacing, z_spacing_original),
                         interplator=sitk.sitkNearestNeighbor)
        label = pad_crop(label, output_size=(512, 512, z_size_original))

        uid = Parser.get_id_from_name(ct.stem)
        sitk.WriteImage(img, os.path.join(output_folder, 'case_' + str(uid).zfill(4) + '.nrrd'))
        sitk.WriteImage(label, os.path.join(output_folder, 'case_' + str(uid).zfill(4) + '_label.nrrd'), True)

        d.append((
            {
                "case_uid": uid,
                "slices": z_size_original
            }

        ))

    pd.DataFrame(d).to_csv(os.path.join(sheets_folder, image_set + '.csv'), index=False)
