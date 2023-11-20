from keras.layers import Input, Conv3D, BatchNormalization, \
    Activation, MaxPooling3D, UpSampling3D, concatenate
from keras.models import Model
from keras.regularizers import l2

class UNet3D:
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
        conv = Conv3D(nb_filter, (kernel_dim1, kernel_dim2, kernel_dim3),
                      kernel_initializer='he_normal',
                      activation=None,
                      padding='same',
                      kernel_regularizer=l2(self.l2))(x)
        if self.bn:
            conv = BatchNormalization(momentum=0.9, axis=-1)(conv)
        x = self.activation_layer(conv)
        return x

    def u_route(self, x):
        filter_factor = self.filter_factor

        # Contracting Path (Encoder)
        conv1 = self.conv_bn_relu(x, filter_factor * 8, 3, 3, 3)
        conv1 = self.conv_bn_relu(conv1, filter_factor * 8, 3, 3, 3)
        pool1 = MaxPooling3D(pool_size=(2, 2, 2))(conv1)

        conv2 = self.conv_bn_relu(pool1, filter_factor * 16, 3, 3, 3)
        conv2 = self.conv_bn_relu(conv2, filter_factor * 16, 3, 3, 3)
        pool2 = MaxPooling3D(pool_size=(2, 2, 2))(conv2)

        conv3 = self.conv_bn_relu(pool2, filter_factor * 32, 3, 3, 3)
        conv3 = self.conv_bn_relu(conv3, filter_factor * 32, 3, 3, 3)
        pool3 = MaxPooling3D(pool_size=(2, 2, 2))(conv3)

        # Bottleneck
        conv4 = self.conv_bn_relu(pool3, filter_factor * 64, 3, 3, 3)
        conv4 = self.conv_bn_relu(conv4, filter_factor * 64, 3, 3, 3)

        # Expansive Path (Decoder)
        up5 = concatenate([UpSampling3D(size=(2, 2, 2))(conv4), conv3], axis=-1)
        conv5 = self.conv_bn_relu(up5, filter_factor * 32, 3, 3, 3)
        conv5 = self.conv_bn_relu(conv5, filter_factor * 32, 3, 3, 3)

        up6 = concatenate([UpSampling3D(size=(2, 2, 2))(conv5), conv2], axis=-1)
        conv6 = self.conv_bn_relu(up6, filter_factor * 16, 3, 3, 3)
        conv6 = self.conv_bn_relu(conv6, filter_factor * 16, 3, 3, 3)

        up7 = concatenate([UpSampling3D(size=(2, 2, 2))(conv6), conv1], axis=-1)
        conv7 = self.conv_bn_relu(up7, filter_factor * 8, 3, 3, 3)
        conv7 = self.conv_bn_relu(conv7, filter_factor * 8, 3, 3, 3)

        # Final Convolution Layer
        conv_final = Conv3D(self.n_classes, (1, 1, 1), activation=self.non_linearity)(conv7)

        return conv_final


    def model(self):
        image_3d = Input((None, None, None, 1))  # Adjust the input shape as per your data
        output_layer = self.u_route(image_3d)
        model = Model(inputs=image_3d, outputs=output_layer)
        return model

if __name__ == "__main__":
    from keras.utils import plot_model
    unet3d = UNet3D()
    model3d = unet3d.model()
    plot_model(model3d, 'model_3d.png', show_shapes=True, show_layer_names=True)