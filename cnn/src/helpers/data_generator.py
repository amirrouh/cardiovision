import numpy as np
import os
from tensorflow.keras.utils import Sequence

class DataGenerator(Sequence):
    def __init__(self, set_dir, data_type, batch_size):
        self.set_dir = set_dir
        if data_type == 'train':
            self.slice_nrs = np.load(os.path.join(self.set_dir, 'X_train_slices.npy'))
        else:
            self.slice_nrs = np.load(os.path.join(self.set_dir, 'X_validation_slices.npy'))
        self.x = self.slice_nrs[:,0]
        self.y = self.slice_nrs[:,1]
        self.batch_size = batch_size
        self.data_type = data_type

    def __len__(self):
        return int(np.ceil(len(self.x) / float(self.batch_size)))

    def __getitem__3d(self, idx):
        for i in range(self.batch_size):
            x = np.load(os.path.join(self.set_dir, 'X_train/', self.x[idx*self.batch_size+i]))
            y = np.load(os.path.join(self.set_dir, 'y_train/', self.y[idx*self.batch_size+i]))
            if i == 0:
                batch_x = x
                batch_y = y
            else:
                batch_x = np.concatenate((batch_x, x), axis=0)
                batch_y = np.concatenate((batch_y, y), axis=0)
        print(batch_x.shape)
        return batch_x, batch_y
    def __getitem__(self, idx):
        files = self.x[self.batch_size*idx:self.batch_size*(idx+1)]
        slices = self.y[self.batch_size*idx:self.batch_size*(idx+1)]
        first = 0
        for f in np.unique(files):
            x = np.load(os.path.join(self.set_dir, 'X_train/X_train'+str(f).zfill(4) +'.npy'))[slices[files==f],:,:,0]
            y = np.load(os.path.join(self.set_dir, 'y_train/y_train'+str(f).zfill(4) +'.npy'))[slices[files==f],:,:,:]
            # y = np.load(os.path.join(self.set_dir, 'y_train/y_train'+str(f).zfill(4) +'.npy'))[np.min(files[files==f,1]):np.max(files[files[:,0]==f,1])+1,:,:,:]
            if first == 0:
                batch_x = x
                batch_y = y
                first = 1
            else:
                batch_x = np.concatenate((batch_x, x), axis=0)
                batch_y = np.concatenate((batch_y, y), axis=0)
        return batch_x, batch_y
    
class DataGenerator2(Sequence):
    def __init__(self, x_set, y_set, batch_size):
        self.x, self.y = x_set, y_set
        self.batch_size = batch_size

    def __len__(self):
        return int(np.ceil(len(self.x) / float(self.batch_size)))

    def __getitem__(self, idx):
        batch_x = self.x[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_y = self.y[idx * self.batch_size:(idx + 1) * self.batch_size]
        return batch_x, batch_y