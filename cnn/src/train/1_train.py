print('updated version 2.2')
import os
import sys

import numpy as np
from tensorflow.keras.callbacks import ModelCheckpoint, CSVLogger, ReduceLROnPlateau, EarlyStopping
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import plot_model

np.random.seed(17)
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0, 1"
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

this_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_directory, '..', '..', '..'))

from utils.io import FileFolders as ff
folders = ff.folders

models_folder = folders['cnn']['models']
arrays_folder = folders['cnn']['arrays']

from cnn.src.helpers.custom_loss import DiceLoss, LabelDice
from cnn.src.helpers.unet import UNet
from cnn.src.helpers.data_generator import DataGenerator


n_classes = 2
n_ensembles = 1


if __name__ == '__main__':
    image_set = 'set_1'
    experiment = 'unet2d'

    input_folder = os.path.join(arrays_folder, image_set)
    output_folder = os.path.join(models_folder, image_set + '_' + experiment)
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)
    folds = sorted(os.listdir(input_folder))
    for fold in folds:
        for seed in range(17, 17 + n_ensembles):
            if int(fold + str(seed)) <517:
                continue
            print('running for fold {} seed {}'.format(fold, seed))
            output_fold_folder = os.path.join(output_folder, fold + '_' + str(seed))
            print(f'output folder: {output_fold_folder}')
            if not os.path.isdir(output_fold_folder):
                os.mkdir(output_fold_folder)
            cnn = UNet(n_classes=n_classes)
            model = cnn.model()
            input_fold_folder = os.path.join(input_folder, fold)

            callbacks_list = list()

            csv_logger = CSVLogger(os.path.join(output_fold_folder, 'log.csv'))
            callbacks_list.append(csv_logger)

            model_checkpoint = ModelCheckpoint(os.path.join(output_fold_folder, 'model_checkpoint.hdf5'),
                                               monitor='val_loss', save_best_only=True, verbose=True)
            callbacks_list.append(model_checkpoint)

            reduce_lr = ReduceLROnPlateau(monitor="val_loss",
                                          factor=0.8,
                                          patience=20,
                                          min_delta=1e-3,
                                          min_lr=1e-6,
                                          verbose=1)
            callbacks_list.append(reduce_lr)

            es = EarlyStopping(monitor='val_loss', min_delta=1e-4, patience=30, verbose=1)
            callbacks_list.append(es)

            plot_model(model, to_file=os.path.join(output_fold_folder, 'model.png'), show_shapes=True)
            with open(os.path.join(output_fold_folder, 'summary.txt'), 'w') as fh:
                model.summary(print_fn=lambda x: fh.write(x + '\n'))

            # loss function

            d = DiceLoss(n_classes=n_classes, smooth=1)
            loss = d.loss

            # metrics
            label_0_dice = LabelDice(label_value=0).dice
            label_1_dice = LabelDice(label_value=1).dice

            optimizer = Adam(learning_rate=1e-3)

            # compiling model
            print('compiling model ...')
            model.compile(optimizer=optimizer,
                          loss=loss,
                          metrics=[label_1_dice],
                          )
            #model.metrics_names = ['loss', 'bg_dice']
            print('fit model')

            train_gen = DataGenerator(input_fold_folder,'train', 1)
            validation_gen = DataGenerator(input_fold_folder, 'validation', 1)
            model.fit(train_gen,
                      epochs=300,
                      verbose=True,
                      shuffle=True,
                      callbacks=callbacks_list,
                      validation_data=validation_gen)
