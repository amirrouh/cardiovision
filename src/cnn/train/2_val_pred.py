import os
import sys

import SimpleITK as sitk
import numpy as np
import pandas as pd
from tqdm import tqdm

np.random.seed(17)
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

sys.path.append('..')
from cnn.initialization.create_folders import sheets_folder, models_folder, images_folder
from cnn.helpers.unet import UNet

n_classes = 2

if __name__ == '__main__':
    image_set = 'set_1'
    experiment = 'unet2d'
    train_uid = image_set + '_' + experiment

    csv_path = os.path.join(sheets_folder, image_set + '_split.csv')
    df = pd.read_csv(csv_path)

    cnn = UNet(n_classes=n_classes)

    model = cnn.model()
    for fold in range(1, 6):
        df_filtered = df[df.fold == fold]
        for case_uid in df_filtered.case_uid.values:
            img_path = os.path.join(images_folder, image_set, 'case_' + str(case_uid).zfill(4) + '.nrrd')
            img = sitk.ReadImage(img_path)
            X = sitk.GetArrayFromImage(img)
            X = np.expand_dims(X, axis=-1).astype(np.float32)
            #
            checkpoint_filename = 'model_checkpoint.hdf5'

            train_folder = os.path.join(models_folder, train_uid)
            models = [folder for folder in sorted(os.listdir(train_folder)) if folder.startswith(str(fold))]
            print(models)
            for model_folder in tqdm(models):
                if model_folder.startswith(str(fold)):
                    model_checkpoint = os.path.join(models_folder, train_uid, model_folder, checkpoint_filename)
                    output_folder = os.path.join(models_folder, train_uid, model_folder, 'val_pred')
                    if not os.path.isdir(output_folder):
                        os.mkdir(output_folder)
                    model.load_weights(model_checkpoint)
                    pred_nda = model.predict(X, batch_size=64, verbose=False)
                    for i in range(n_classes):
                        pred_tmp = pred_nda[..., i]
                        pred_image = sitk.GetImageFromArray(pred_tmp)
                        pred_image.CopyInformation(img)
                        sitk.WriteImage(pred_image, os.path.join(output_folder,  'case_' +
                                                                 str(case_uid).zfill(4) + '_pred_' +
                                                                 str(i) + '.nrrd'), True)
