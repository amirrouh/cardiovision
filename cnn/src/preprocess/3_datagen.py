import os
import sys

import SimpleITK as sitk
import numpy as np
import pandas as pd

from tqdm import tqdm

np.random.seed(17)

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..', '..'))

from utils.io import FileFolders as ff
folders = ff.folders

from dataaug import AugmentImage

sheets_folder = folders['cnn']['sheets']
arrays_folder = folders['cnn']['arrays']
images_folder = folders['cnn']['images']

n_classes = 2
if __name__ == '__main__':
    image_set = 'set_1'

    csv_path = os.path.join(sheets_folder, image_set + '_split.csv')

    image_folder = os.path.join(images_folder, image_set)

    df = pd.read_csv(csv_path)
    folds = sorted(df.fold.unique())

    output_folder = os.path.join(arrays_folder, image_set)
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    for fold in folds:
        if fold > 0:
            print('processing fold {}'.format(fold))
            output_fold_folder = os.path.join(output_folder, str(int(fold)))
            if not os.path.isdir(output_fold_folder):
                os.mkdir(output_fold_folder)
            if not os.path.isdir(os.path.join(output_fold_folder,'X_train/')):
                os.mkdir(os.path.join(output_fold_folder,'X_train/'))
            if not os.path.isdir(os.path.join(output_fold_folder, 'y_train/')):
                os.mkdir(os.path.join(output_fold_folder,'y_train/'))
            for data_type in ['train', 'validation']:
                if data_type == 'train':
                    df_filtered = df[df.fold != fold]
                    name_idx = np.arange(len(df_filtered)*6)
                    np.random.shuffle(name_idx)
                    name_idx = name_idx.reshape(len(df_filtered), 6)
                    name_counter = 0
                    for index, row in tqdm(df_filtered.iterrows(), total=len(df_filtered)):
                        img_path = os.path.join(image_folder, 'case_' + str(row.case_uid).zfill(4) + '.nrrd')
                        img = sitk.ReadImage(img_path)
                        label = sitk.ReadImage(img_path.replace('.nrrd', '_label.nrrd'))
                        
                        # data augmentation
                        img_aug, label_aug = AugmentImage.augment_image(img, 
                                                                        ((0,0), (0,0), (-np.pi, np.pi)), 
                                                                        ((-1, 1), (-1, 1), (0, 0)), 
                                                                        label, 5, np.amin(sitk.GetArrayFromImage(img)))
                        
                        for counter in range(len(img_aug)+1):
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

                            # if name_counter == 0:
                            #     X = img_nda
                            #     y = label_nda_multi_class
                            #     name_counter = 1
                            # else:
                            #     X = np.concatenate((X, img_nda), axis=0)
                            #     y = np.concatenate((y, label_nda_multi_class), axis=0)
                        
                    # X = np.expand_dims(X, axis=-1).astype(np.float32)

                    # # y = np.concatenate((y, np.fliplr(y)), axis=0).\
                    # y = y.astype(np.float32)

                    # np.save(os.path.join(output_fold_folder, 'X_' + data_type + '.npy'), X)
                    # np.save(os.path.join(output_fold_folder, 'y_' + data_type + '.npy'), y)
                            
                            
                            X = np.expand_dims(img_nda, axis=-1).astype(np.float32)
                            y = label_nda_multi_class.astype(np.float32)
                            np.save(os.path.join(output_fold_folder, 'X_train/X_' + data_type + str(name_idx[name_counter, counter]).zfill(4) + '.npy'), X)
                            np.save(os.path.join(output_fold_folder, 'y_train/y_' + data_type + str(name_idx[name_counter, counter]).zfill(4) + '.npy'), y)
                            
                            if X.shape[0] != y.shape[0]:
                                print(f'error for {row.case_uid}, shapes do not match')
                            
                            nr_slices_arr = np.repeat(np.array([name_idx[name_counter, counter]]), X.shape[0])
                            nr_slices_arr = nr_slices_arr.reshape((X.shape[0], 1))
                            nr_slices_arr = np.concatenate((nr_slices_arr, np.arange(X.shape[0]).reshape((X.shape[0], 1))), axis=1)
                            if counter == 0 and name_counter == 0:
                                nr_slices = nr_slices_arr
                            else:
                                nr_slices = np.concatenate((nr_slices, nr_slices_arr), axis = 0)
                        name_counter += 1
                    nr_slices = nr_slices[nr_slices[:, 1].argsort()]
                    nr_slices = nr_slices[nr_slices[:, 0].argsort(kind='mergesort')]
                    np.save(os.path.join(output_fold_folder, 'X_train_slices.npy'), nr_slices)
                else:
                    df_filtered = df[df.fold == fold]
                    counter = 0
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

                        if counter == 0:
                            X = img_nda
                            y = label_nda_multi_class
                        else:
                            X = np.concatenate((X, img_nda), axis=0)
                            y = np.concatenate((y, label_nda_multi_class), axis=0)
                        counter += 1

                    # todo: 35 set1 did not fit into the memeroy
                    # X = np.concatenate((X, np.fliplr(X)), axis=0)
                    X = np.expand_dims(X, axis=-1).astype(np.float32)

                    # y = np.concatenate((y, np.fliplr(y)), axis=0).\
                    y = y.astype(np.float32)

                    np.save(os.path.join(output_fold_folder, 'X_' + data_type + '.npy'), X)
                    np.save(os.path.join(output_fold_folder, 'y_' + data_type + '.npy'), y)
