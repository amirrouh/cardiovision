import os
import sys

import SimpleITK as sitk
import pandas as pd
from tqdm import tqdm

sys.path.append('..')

from cnn.initialization.create_folders import images_folder, sheets_folder, Parameters

from cnn.helpers.utils import resample, pad_crop, Parser

if __name__ == '__main__':
    image_set = "set_1"
    cts_dir = Parameters.input_dir/'images'
    cts = list(cts_dir.glob('*.nrrd'))
    cts.sort()
    lbls_dir = Parameters.input_dir/'labels'
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
