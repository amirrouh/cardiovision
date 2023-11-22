import os
import sys

import SimpleITK as sitk
import numpy as np
import pandas as pd

from tqdm import tqdm

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..', '..'))

from utils.io import FileFolders as ff
folders = ff.folders

from cnn.src.preprocess.dataaug import AugmentImage

sheets_folder = folders['cnn']['sheets']
arrays_folder = folders['cnn']['arrays']
images_folder = folders['cnn']['images']


def data_generator(data_type, fold, batch_size, image_set, n_classes = 2):

    csv_path = os.path.join(sheets_folder, image_set + '_split.csv')

    image_folder = os.path.join(images_folder, image_set)

    df = pd.read_csv(csv_path)

    output_folder = os.path.join(arrays_folder, image_set)
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    if data_type == 'train':
        df_filtered = df[df.fold != fold]
        batch_counter = 0
        X_batch = False
        for index, row in tqdm(df_filtered.iterrows(), total=len(df_filtered)):
            img_path = os.path.join(image_folder, 'case_' + str(row.case_uid).zfill(4) + '.nrrd')
            img = sitk.ReadImage(img_path)
            label = sitk.ReadImage(img_path.replace('.nrrd', '_label.nrrd'))
            
            # data augmentation
            img_aug, label_aug = AugmentImage.augment_image(img, 
                                                            ((0,0), (0,0), (-np.pi/6, np.pi/6)), 
                                                            ((-1, 1), (-1, 1), (0, 0)), 
                                                            label, 5, np.amin(sitk.GetArrayFromImage(img)),
                                                            seed=index*1000)

            for counter in range(6):
                if counter == 0:
                    img_nda = sitk.GetArrayFromImage(img)
                    label_nda = sitk.GetArrayFromImage(label)
                else:
                    img_nda = sitk.GetArrayFromImage(img_aug[counter-1])
                    label_nda = sitk.GetArrayFromImage(label_aug[counter-1])
                shape = label_nda.shape
                label_nda_multi_class = np.zeros((shape[0], shape[1], shape[2], n_classes))

                for i in range(n_classes):
                    tmp = np.copy(label_nda)
                    tmp[tmp != i] = 255
                    tmp[tmp == i] = 1
                    label_nda_multi_class[..., i] = tmp
                label_nda_multi_class[label_nda_multi_class == 255] = 0
    
                X = np.expand_dims(img_nda, axis=-1).astype(np.float32)
                y = label_nda_multi_class.astype(np.int8)

                if type(X_batch) == bool:
                    for i in range(0, X.shape[0], batch_size):
                        X_batch = X[i:i + batch_size]
                        y_batch = y[i:i + batch_size]
                        if X_batch.shape[0] >= batch_size:
                            np.save(os.path.join(output_folder, 'X_train/X_' + data_type + str(batch_counter).zfill(5) + '.npy'), X_batch)
                            np.save(os.path.join(output_folder, 'y_train/y_' + data_type + str(batch_counter).zfill(5) + '.npy'), y_batch)
                            batch_counter += 1
                            X_batch = False
                else:
                    start_idx = X_batch.shape[0]
                    X_batch = np.concatenate((X_batch, X[:(batch_size-start_idx)]), axis=0)
                    y_batch = np.concatenate((y_batch, y[:(batch_size-start_idx)]), axis=0)
                    for i in range(batch_size-start_idx, X.shape[0], batch_size):
                        X_batch = X[i:i + batch_size]
                        y_batch = y[i:i + batch_size]
                        if X_batch.shape[0] >= batch_size:
                            np.save(os.path.join(output_folder, 'X_train/X_' + data_type + str(batch_counter).zfill(5) + '.npy'), X_batch)
                            np.save(os.path.join(output_folder, 'y_train/y_' + data_type + str(batch_counter).zfill(5) + '.npy'), y_batch)
                            batch_counter += 1
                            X_batch = False
        if type(X_batch) != bool:
            np.save(os.path.join(output_folder, 'X_train/X_' + data_type + str(batch_counter).zfill(5) + '.npy'), X_batch)
            np.save(os.path.join(output_folder, 'y_train/y_' + data_type + str(batch_counter).zfill(5) + '.npy'), y_batch.astype(np.int8))
    if data_type == 'validation':
        df_filtered = df[df.fold == fold]
        X_batch = False
        batch_counter = 0
        for index, row in tqdm(df_filtered.iterrows(), total=len(df_filtered)):
            img_path = os.path.join(image_folder, 'case_' + str(row.case_uid).zfill(4) + '.nrrd')
            img = sitk.ReadImage(img_path)
            label = sitk.ReadImage(img_path.replace('.nrrd', '_label.nrrd'))

            img_nda = sitk.GetArrayFromImage(img)
            label_nda = sitk.GetArrayFromImage(label)

            shape = label_nda.shape
            label_nda_multi_class = np.zeros((shape[0], shape[1], shape[2], n_classes))

            for i in range(n_classes):
                tmp = np.copy(label_nda)
                tmp[tmp != i] = 255
                tmp[tmp == i] = 1
                label_nda_multi_class[..., i] = tmp
            label_nda_multi_class[label_nda_multi_class == 255] = 0

            X = np.expand_dims(img_nda, axis=-1).astype(np.float32)
            y = label_nda_multi_class.astype(np.int8)

            if type(X_batch) == bool:
                for i in range(0, X.shape[0], batch_size):
                    X_batch = X[i:i + batch_size]
                    y_batch = y[i:i + batch_size]
                    if X_batch.shape[0] >= batch_size:
                        np.save(os.path.join(output_folder, 'X_validation/X_' + data_type + str(batch_counter).zfill(5) + '.npy'), X_batch)
                        np.save(os.path.join(output_folder, 'y_validation/y_' + data_type + str(batch_counter).zfill(5) + '.npy'), y_batch)
                        batch_counter += 1
                        X_batch = False
            else:
                start_idx = X_batch.shape[0]
                X_batch = np.concatenate((X_batch, X[:(batch_size-start_idx)]), axis=0)
                y_batch = np.concatenate((y_batch, y[:(batch_size-start_idx)]), axis=0)
                for i in range(batch_size-start_idx, X.shape[0], batch_size):
                    X_batch = X[i:i + batch_size]
                    y_batch = y[i:i + batch_size]
                    if X_batch.shape[0] >= batch_size:
                        np.save(os.path.join(output_folder, 'X_validation/X_' + data_type + str(batch_counter).zfill(5) + '.npy'), X_batch)
                        np.save(os.path.join(output_folder, 'y_validation/y_' + data_type + str(batch_counter).zfill(5) + '.npy'), y_batch)
                        batch_counter += 1
                        X_batch = False
        if type(X_batch) != bool:
            np.save(os.path.join(output_folder, 'X_validation/X_' + data_type + str(batch_counter).zfill(5) + '.npy'), X_batch)
            np.save(os.path.join(output_folder, 'y_validation/y_' + data_type + str(batch_counter).zfill(5) + '.npy'), y_batch.astype(np.int8))