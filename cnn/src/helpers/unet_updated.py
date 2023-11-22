from keras.layers import Input, Convolution2D, BatchNormalization, \
    Activation, MaxPooling2D, UpSampling2D, concatenate
from keras.models import Model
from keras.regularizers import l2


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

    def conv_bn_relu(self, x, nb_filter, kernel_dim1, kernel_dim2):
        conv = Convolution2D(nb_filter, (kernel_dim1, kernel_dim2),
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

    def res_block(self, x, nb_filter, kernel_dim1, kernel_dim2):
        conv = Convolution2D(nb_filter, (kernel_dim1, kernel_dim2),
                             kernel_initializer='he_normal',
                             activation='relu',
                             padding='same',
                             kernel_regularizer=l2(self.l2),
                             bias_regularizer=None,
                             activity_regularizer=None)(x)
        conv = Convolution2D(nb_filter, (kernel_dim1, kernel_dim2),
                             kernel_initializer='he_normal',
                             activation='relu',
                             padding='same',
                             kernel_regularizer=l2(self.l2),
                             bias_regularizer=None,
                             activity_regularizer=None)(conv)
        return conv

    def u_route(self, x):
        filter_factor = self.filter_factor

        # Encoder
        conv1 = self.res_block(x, filter_factor * 8, 3, 3)
        pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

        conv2 = self.res_block(pool1, filter_factor * 16, 3, 3)
        pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

        conv3 = self.res_block(pool2, filter_factor * 32, 3, 3)
        pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

        # Decoder with skip connections
        up4 = concatenate([UpSampling2D(size=(2, 2))(conv3), conv2], axis=-1)
        conv4 = self.res_block(up4, filter_factor * 16, 3, 3)

        up5 = concatenate([UpSampling2D(size=(2, 2))(conv4), conv1], axis=-1)
        conv5 = self.res_block(up5, filter_factor * 8, 3, 3)

        # Output layer
        conv10 = Convolution2D(self.n_classes, (1, 1), activation=self.non_linearity)(conv5)
        return conv10

    def model(self):
        image_1 = Input((512, 512, 1))
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