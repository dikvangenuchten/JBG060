import os
import tensorflow as tf
from tensorflow.keras.layers import Conv1D, Flatten, Dense


class DiffPredictor(tf.keras.Model):
    def __init__(self, pump_station):
        super().__init__()
        self.conv_1 = Conv1D(4, kernel_size=6, activation="relu", padding="same")
        self.conv_2 = Conv1D(2, kernel_size=6, activation="relu", padding="same")
        self.conv_3 = Conv1D(1, kernel_size=3, activation="relu", padding="same")
        self.pump_station = pump_station

    def call(self, inputs, training=None, mask=None):
        x = self.conv_1(inputs)
        x = self.conv_2(x)
        x = self.conv_3(x)
        return tf.squeeze(x, axis=-1)

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
