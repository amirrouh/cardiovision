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
            for data_type in ['train', 'validation']:
                if data_type == 'train':
                    df_filtered = df[df.fold != fold]
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

                # if data_type == 'train':
                #     import matplotlib.pyplot as plt
                #     fig = plt.figure()
                #     y_concat = np.sum(y[..., 1], axis=0)
                #     plt.imshow(y_concat)
                #     plt.show()
                #     plt.close(fig)
