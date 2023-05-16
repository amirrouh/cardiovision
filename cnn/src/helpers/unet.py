from tensorflow.keras.layers import Input, Convolution3D, BatchNormalization, \
    Activation, MaxPooling3D, UpSampling3D, concatenate
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2


class UNet:
    def __init__(self, filter_factor=1, n_classes=2,
                 dropout=False,
                 bn=True,
                 l2=1e-4, non_linearity='sigmoid'):
        self.filter_factor = filter_factor
        self.n_classes = n_classes
        self.dropout = dropout
        self.bn = bn
        self.l2 = l2
        self.non_linearity = non_linearity

    def activation_layer(self, x):
        return Activation("relu")(x)

    def conv_bn_relu(self, x, nb_filter, kernel_dim1, kernel_dim2, kernel_dim3):
        conv = Convolution3D(nb_filter, (kernel_dim1, kernel_dim2, kernel_dim3),
                             kernel_initializer='he_normal',
                             activation=None,
                             padding='same',
                             kernel_regularizer=l2(self.l2),
                             bias_regularizer=None,
                             activity_regularizer=None)(x)
        if self.bn:
            conv = BatchNormalization(momentum=0.9, axis=-1)(conv)
        x = self.activation_layer(conv)
        return x

    def u_route(self, x):
        filter_factor = self.filter_factor
        conv1 = self.conv_bn_relu(x, filter_factor * 4, 3, 3, 3)
        conv1 = self.conv_bn_relu(conv1, filter_factor * 4, 3, 3, 3)
        pool1 = MaxPooling3D(pool_size=(4, 4, 4))(conv1)

        conv2 = self.conv_bn_relu(pool1, filter_factor * 8, 3, 3, 3)
        conv2 = self.conv_bn_relu(conv2, filter_factor * 8, 3, 3, 3)
        pool2 = MaxPooling3D(pool_size=(4, 4, 4))(conv2)

        conv3 = self.conv_bn_relu(pool2, filter_factor * 16, 3, 3, 3)
        conv3 = self.conv_bn_relu(conv3, filter_factor * 16, 3, 3, 3)
        pool3 = MaxPooling3D(pool_size=(4, 4, 4))(conv3)

        conv5 = self.conv_bn_relu(pool3, filter_factor * 32, 3, 3, 3)
        conv5 = self.conv_bn_relu(conv5, filter_factor * 32, 3, 3, 3)

        up6 = concatenate([UpSampling3D(size=(4, 4, 4))(conv5), conv3], axis=-1)
        conv6 = self.conv_bn_relu(up6, filter_factor * 16, 3, 3, 3)
        conv6 = self.conv_bn_relu(conv6, filter_factor * 16, 3, 3, 3)

        up7 = concatenate([UpSampling3D(size=(4, 4, 4))(conv6), conv2], axis=-1)
        conv7 = self.conv_bn_relu(up7, filter_factor * 8, 3, 3, 3)
        conv7 = self.conv_bn_relu(conv7, filter_factor * 8, 3, 3, 3)

        up8 = concatenate([UpSampling3D(size=(4, 4, 4))(conv7), conv1], axis=-1)
        conv8 = self.conv_bn_relu(up8, filter_factor * 4, 3, 3, 3)
        conv8 = self.conv_bn_relu(conv8, filter_factor * 4, 3, 3, 3)

        conv10 = Convolution3D(self.n_classes, (1, 1, 1), activation=self.non_linearity)(conv8)
        return conv10

    def model(self):
        image_1 = Input((128, 256, 256, 1))
        non_linearity_output = self.u_route(image_1)
        model = Model(inputs=image_1, outputs=non_linearity_output)
        return model

if __name__ == "__main__":
    from main_run.global_settings import shared_dir
    from keras.utils import plot_model
    from neuralplot import ModelPlot
    unet = UNet()
    model = unet.model()
    # plot_model(model, str(shared_dir / 'model.png'), show_shapes=True, show_layer_names=True)
    modelplot = ModelPlot(model=model, grid=True, connection=True, linewidth=0.1)
    modelplot.show()

