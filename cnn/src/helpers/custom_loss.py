from tensorflow.keras import backend as K


class LabelDice:
    def __init__(self, label_value, smooth=1e-3):
        self.label_value = label_value
        self.smooth = smooth

    def dice(self, y_true, y_pred):
        y_true_f = K.flatten(y_true[..., self.label_value])
        y_pred_f = K.flatten(y_pred[..., self.label_value])
        intersection = K.sum(y_true_f * y_pred_f)
        union = K.sum(y_true_f) + K.sum(y_pred_f)
        return (2. * intersection + self.smooth) / (union + self.smooth)


class DiceLoss:
    def __init__(self, n_classes, smooth):
        self.n_classes = n_classes
        self.smooth = smooth

    def dice(self, y_true, y_predicted):
        y_true_f = K.flatten(y_true)
        y_pred_f = K.flatten(y_predicted)
        intersection = K.sum(y_true_f * y_pred_f)
        union = K.sum(y_true_f) + K.sum(y_pred_f)
        dice = (2. * intersection + self.smooth) / (union + self.smooth)
        return dice

    def loss(self, y_true, y_pred):
        # loss = 0
        # for i in range(1, self.n_classes):
        #     loss -= self.dice(y_true[..., i], y_pred[..., i])
        return -self.dice(y_true[..., 1], y_pred[..., 1])