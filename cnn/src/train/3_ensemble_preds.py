import os
import shutil
import sys

import SimpleITK as sitk
import numpy as np
import pandas as pd
from tqdm import tqdm

np.random.seed(17)

sys.path.append('..')
from cnn.initialization.create_folders import sheets_folder, models_folder, images_folder

THRESHOLD = 0.5

if __name__ == '__main__':
    image_set = 'pilot'
    image_set = 'set_1'
    experiment = 'unet2d'
    train_uid = image_set + '_' + experiment

    n_classes = 2

    csv_path = os.path.join(sheets_folder, image_set + '_split.csv')
    df = pd.read_csv(csv_path)
    pred_folders = ['val_pred', 'test_pred']
    pred_folders = ['val_pred']
    for fold in range(1, 6):
        for pred_folder in pred_folders:
            df_filtered = df[df.fold == fold]
            for case_uid in df_filtered.case_uid.values:
                try:
                    img_path = os.path.join(images_folder, image_set, 'case_' + str(case_uid).zfill(4) + '.nrrd')
                    train_folder = os.path.join(models_folder, train_uid)
                    models = [folder for folder in sorted(os.listdir(train_folder)) if folder.startswith(str(fold))]
                    output_folder = os.path.join(models_folder, train_uid, 'mean_std_' + str(fold), pred_folder)
                    if not os.path.isdir(output_folder):
                        os.makedirs(output_folder)
                    sample_path = os.path.join(models_folder, train_uid,
                                               models[0], pred_folder,
                                               'case_' + str(case_uid).zfill(4) + '_pred_1.nrrd')

                    print(sample_path)
                    pred_sample = sitk.ReadImage(sample_path)
                    pred_nda = sitk.GetArrayFromImage(pred_sample)
                    nda = np.zeros((*pred_nda.shape, len(models)))
                    for label_value in range(n_classes):
                        for index, model_folder in enumerate(tqdm(models)):
                            pred = sitk.ReadImage(os.path.join(models_folder, train_uid,
                                                               model_folder, pred_folder,
                                                               'case_' + str(case_uid).zfill(4) + '_pred_' +
                                                               str(label_value) + '.nrrd'))
                            nda[..., index] = sitk.GetArrayFromImage(pred)
                        nda_mean = np.mean(nda, axis=-1)
                        image_mean = sitk.GetImageFromArray(nda_mean)
                        image_mean.CopyInformation(pred)
                        sitk.WriteImage(image_mean, os.path.join(output_folder, 'case_' + str(case_uid).zfill(4) + '_mean' +
                                                                 str(label_value) + '.nrrd'), True)

                        pred_image_th = sitk.BinaryThreshold(image_mean, lowerThreshold=THRESHOLD, upperThreshold=1,
                                                             insideValue=1, outsideValue=0)
                        sitk.WriteImage(pred_image_th, os.path.join(output_folder, 'case_' +
                                                                    str(case_uid).zfill(4) + '_mean_th' +
                                                                    str(label_value) + '.nrrd'), True)
                    shutil.copy(img_path, os.path.join(output_folder, os.path.basename(img_path)))
                    label_path = img_path.replace('.nrrd', '_label.nrrd')
                    shutil.copy(label_path, os.path.join(output_folder, os.path.basename(label_path)))
                except:
                    print(f'fold {fold} folder does not exist')
