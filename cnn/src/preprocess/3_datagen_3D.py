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

    def process_volume(img_path, label_path, n_classes):
        img = sitk.ReadImage(img_path)
        label = sitk.ReadImage(label_path)

        img_nda = sitk.GetArrayFromImage(img)  # Convert image to NumPy array
        label_nda = sitk.GetArrayFromImage(label)

        img_nda = np.expand_dims(img_nda, axis=-1).astype(np.float32)  # Add channel dimension
        label_nda = label_nda.astype(np.uint8)

        # Multi-class label processing
        label_nda_multi_class = np.zeros((*label_nda.shape, n_classes))
        for i in range(n_classes):
            label_nda_multi_class[..., i] = (label_nda == i).astype(np.uint8)

        return img_nda, label_nda_multi_class

    print(f"folds={folds}")
    print("start generating folds 3D")
    for fold in folds:
        if fold > 0:
            print('processing fold {}'.format(fold))
            output_fold_folder = os.path.join(output_folder, str(int(fold)))
            if not os.path.isdir(output_fold_folder):
                os.mkdir(output_fold_folder)

            for data_type in ['train', 'validation']:
                print(f'processing {data_type} data')
                if data_type == 'train':
                    df_filtered = df[df.fold != fold]
                else:
                    df_filtered = df[df.fold == fold]

                volumes_X = []
                volumes_y = []

                for index, row in tqdm(df_filtered.iterrows(), total=len(df_filtered)):
                    img_path = os.path.join(image_folder, 'case_' + str(row.case_uid).zfill(4) + '.nrrd')
                    label_path = img_path.replace('.nrrd', '_label.nrrd')

                    img_nda, label_nda = process_volume(img_path, label_path, n_classes)
                    volumes_X.append(img_nda)
                    volumes_y.append(label_nda)

                # Since all volumes are the same size, we can stack them
                X = np.stack(volumes_X, axis=0)
                y = np.stack(volumes_y, axis=0)

                print("Shape of X:", X.shape)
                print("Shape of y:", y.shape)
                print("path: ", output_fold_folder)


                np.save(os.path.join(output_fold_folder, 'X_' + data_type + '.npy'), X)
                np.save(os.path.join(output_fold_folder, 'y_' + data_type + '.npy'), y)


                # if data_type == 'train':
                #     import matplotlib.pyplot as plt
                #     fig = plt.figure()
                #     y_concat = np.sum(y[..., 1], axis=0)
                #     plt.imshow(y_concat)
                #     plt.show()
                #     plt.close(fig)


    print("3_datagen completed")
