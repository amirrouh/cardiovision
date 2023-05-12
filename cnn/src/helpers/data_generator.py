import numpy as np
import os
from tensorflow.keras.utils import Sequence

class DataGenerator(Sequence):
    def __init__(self, set_dir, data_type, batch_size):
        self.set_dir = set_dir
        self.batch_size = batch_size
        if data_type == 'train':
            self.x = [f for f in os.listdir(set_dir + '/X_train/') if f.endswith('.npy')]
            self.y = [f for f in os.listdir(set_dir + '/y_train/') if f.endswith('.npy')]
        elif data_type == 'validation':
            self.x = [f for f in os.listdir(set_dir + '/X_validation/') if f.endswith('.npy')]
            self.y = [f for f in os.listdir(set_dir + '/y_validation/') if f.endswith('.npy')]
        self.data_type = data_type

    def __len__(self):
        return int(np.ceil(len(self.x) / float(self.batch_size)))

    def __getitem__(self, idx):
        for i in range(min(self.batch_size, len(self.x[idx*self.batch_size:idx*self.batch_size+self.batch_size]))):
            if self.data_type == 'train':
                x = np.load(os.path.join(self.set_dir, 'X_train/', self.x[idx*self.batch_size+i]))
                y = np.load(os.path.join(self.set_dir, 'y_train/', self.y[idx*self.batch_size+i]))
            elif self.data_type == 'validation':
                x = np.load(os.path.join(self.set_dir, 'X_validation/', self.x[idx*self.batch_size+i]))
                y = np.load(os.path.join(self.set_dir, 'y_validation/', self.y[idx*self.batch_size+i]))
            if i == 0:
                batch_x = x
                batch_y = y
            else:
                batch_x = np.concatenate((batch_x, x), axis=0)
                batch_y = np.concatenate((batch_y, y), axis=0)
        return batch_x, batch_y