import os
import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from collections import OrderedDict

sys.path.append('../..')

from utils.create_folders import sheets_folder

np.random.seed(17)

if __name__ == '__main__':
    image_set = 'set_1'

    df = pd.read_csv(os.path.join(sheets_folder, image_set + '.csv'))

    patients = df.case_uid.values
    print(patients)
    kf = KFold(n_splits=7, shuffle=True)
    fold = 1
    d = list()
    for _, val_index in kf.split(patients):
        print(fold)
        print(val_index)
        for index in val_index:
            d.append(OrderedDict({"case_uid": patients[index],
                                  "fold": fold}))
        fold += 1
    df = pd.DataFrame(d)
    df.loc[df.fold > 5, 'fold'] = -1
    df.to_csv(os.path.join(sheets_folder, image_set + '_split.csv'), index=False)
