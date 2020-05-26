"""
Networks for voxelwarp model
"""

# third party
import tensorflow as tf
from keras.models import Model
from keras.layers import Conv3D, Activation, Input, UpSampling3D, concatenate, MaxPooling3D, Concatenate
from keras.layers import LeakyReLU, Reshape, Lambda
from keras.initializers import RandomNormal
from keras.regularizers import l2
from parameters import *
import keras
import numpy as np

# local
from network.transformer import Transformer_3D
import network.losses

weight_decay = 1e-4


def reg_unet():
    vol_size = data_shape
    # inputs
    src = Input(shape=vol_size + (1,))
    tgt = Input(shape=vol_size + (1,))
    seg = Input(shape=vol_size + (1,))
    x_in = concatenate([src, tgt])

    conv1 = Conv3D(16, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(x_in)
    print("conv1 shape:", conv1.shape)
    conv1 = Conv3D(16, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(conv1)
    print("conv1 shape:", conv1.shape)
    pool1 = MaxPooling3D(pool_size=(2, 2, 2))(conv1)
    print("pool1 shape:", pool1.shape)

    conv2 = Conv3D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(pool1)
    print("conv2 shape:", conv2.shape)
    conv2 = Conv3D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(conv2)
    print("conv2 shape:", conv2.shape)
    pool2 = MaxPooling3D(pool_size=(2, 2, 2))(conv2)
    print("pool2 shape:", pool2.shape)

    conv3 = Conv3D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(pool2)
    print("conv3 shape:", conv3.shape)
    conv3 = Conv3D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(conv3)
    print("conv3 shape:", conv3.shape)
    # drop3 = Dropout(0.5)(conv3)
    pool3 = MaxPooling3D(pool_size=(2, 2, 2))(conv3)
    print("pool3 shape:", pool3.shape)

    conv4 = Conv3D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(pool3)
    conv4 = Conv3D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(conv4)
    print("conv4 shape:", conv4.shape)
    # drop4 = Dropout(0.5)(conv4)
    pool4 = MaxPooling3D(pool_size=(2, 2, 2))(conv4)
    print("pool4 shape:", pool4.shape)

    conv5 = Conv3D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(pool4)
    conv5 = Conv3D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(conv5)
    print("conv5 shape:", conv5.shape)
    # drop5 = Dropout(0.5)(conv5)
    # print("drop5 shape:", drop5.shape)

    up6 = Conv3D(128, 2, activation='relu', padding='same', kernel_initializer='he_normal',
                 kernel_regularizer=l2(weight_decay))(
        UpSampling3D(size=(2, 2, 2))(conv5))
    print("up6 shape:", up6.shape)
    merge6 = Concatenate(axis=4)([conv4, up6])
    # merge6 = merge([drop4, up6], mode='concat', concat_axis=4)
    print("merge6 shape:", merge6.shape)
    conv6 = Conv3D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(merge6)
    conv6 = Conv3D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(conv6)
    print("conv6 shape:", conv6.shape)

    up7 = Conv3D(64, 2, activation='relu', padding='same', kernel_initializer='he_normal',
                 kernel_regularizer=l2(weight_decay))(
        UpSampling3D(size=(2, 2, 2))(conv6))
    print("up7 shape:", up7.shape)
    merge7 = Concatenate(axis=4)([conv3, up7])
    # merge7 = merge([drop3, up7], mode='concat', concat_axis=4)
    conv7 = Conv3D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(merge7)
    conv7 = Conv3D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(conv7)
    print("conv7 shape:", conv7.shape)

    up8 = Conv3D(32, 2, activation='relu', padding='same', kernel_initializer='he_normal',
                 kernel_regularizer=l2(weight_decay))(
        UpSampling3D(size=(2, 2, 2))(conv7))
    print("up8 shape:", up8.shape)
    merge8 = Concatenate(axis=4)([conv2, up8])
    # merge8 = merge([conv2, up8], mode='concat', concat_axis=4)
    conv8 = Conv3D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(merge8)
    conv8 = Conv3D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(conv8)
    print("conv8 shape:", conv8.shape)

    up9 = Conv3D(16, 2, activation='relu', padding='same', kernel_initializer='he_normal',
                 kernel_regularizer=l2(weight_decay))(
        UpSampling3D(size=(2, 2, 2))(conv8))
    print("up9 shape:", up9.shape)
    merge9 = Concatenate(axis=4)([conv1, up9])
    # merge9 = merge([conv1, up9], mode='concat', concat_axis=4)
    conv9 = Conv3D(16, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(merge9)
    conv9 = Conv3D(16, 3, activation='relu', padding='same', kernel_initializer='he_normal',
                   kernel_regularizer=l2(weight_decay))(conv9)


    # transform the results into a flow.
    flow = Conv3D(3, kernel_size=3, padding='same',
                  kernel_initializer=RandomNormal(mean=0.0, stddev=1e-5), name='flow')(conv9)

    # warp the source with the flow
    y = Transformer_3D()([src, flow])
    segwarped = Transformer_3D()([seg, flow])

    # prepare model
    model = Model(inputs=[src, tgt, seg], outputs=[y, flow, segwarped])
    return model
