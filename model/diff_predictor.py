import os
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Conv2D


class DiffPredictor(tf.keras.Model):
    def __init__(self, pump_station):
        super().__init__()
        self.conv_1 = Conv2D(32, kernel_size=3, activation='relu', input_shape=input_shape)
        self.pump_station = pump_station

    def build(self, input_shape):
        pass

    def call(self, inputs, training=None, mask=None):
        return self.conv_1(inputs)

    def save(self,
             filepath,
             overwrite=True,
             include_optimizer=True,
             save_format=None,
             signatures=None,
             options=None):
        filepath = os.path.join(filepath, self.pump_station)
        super(DiffPredictor, self).save(filepath=filepath,
                                        overwrite=overwrite,
                                        include_optimizer=include_optimizer,
                                        save_format=save_format,
                                        signatures=signatures,
                                        options=options)
