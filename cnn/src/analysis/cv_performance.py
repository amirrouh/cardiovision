# 2d and 3d dice and hd distances
import glob
import os
import sys

import pandas as pd
import SimpleITK as sitk
from collections import OrderedDict

sys.path.append('..')
from cnn.initialization.create_folders import sheets_folder, models_folder
from cnn.helpers.utils import SegmentationQualityMetrics

if __name__ == '__main__':
    # read pandas dataframe
    image_set = 'set_1'
    experiment = 'unet2d'
    train_uid = image_set + '_' + experiment

    d = list()

    # aorta class
    class_val = 1
    output_df_path = os.path.join(sheets_folder, train_uid + '_cv_performance.csv')

    for fold in range(1, 6):
        pred_folder = os.path.join(models_folder, train_uid, 'mean_std_' + str(fold), 'val_pred')
        labels = sorted(glob.glob(pred_folder + '/*_label.nrrd'))
        for ground_truth_path in labels:
            uid = int(os.path.basename(ground_truth_path).split('.')[0].split('_')[1])
            gt_img = sitk.ReadImage(ground_truth_path)
            pred_img_path = ground_truth_path.replace('_label', '_mean_th' + str(class_val))
            pred_img = sitk.ReadImage(pred_img_path)

            sq = SegmentationQualityMetrics(labels={1: "aorta"}, test_image=gt_img,
                                            pred_image=pred_img)
            dice_f = sq.get_dice()
            hd95_f = sq.get_hausdorff()
            dict = OrderedDict(
                {"case_uid": uid,
                 "full_dice": dice_f[1],
                 "full_hd95": hd95_f[1],
                 }
            )
            print(dict)
            d.append(dict)
            pd.DataFrame(d).to_csv(output_df_path, index=False)
