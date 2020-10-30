import os
import tensorflow as tf
from tensorflow.keras.layers import Conv1D, Flatten, Dense


class DiffPredictor(tf.keras.Model):
    def __init__(self, pump_station, input_shape=(None, 48, 3)):
        super().__init__()
        self.conv_1 = Conv1D(12, kernel_size=6, activation="linear", padding="same")
        self.conv_2 = Conv1D(8, kernel_size=6, activation="linear", padding="same")
        self.conv_3 = Conv1D(4, kernel_size=3, activation="linear", padding="same")
        self.flatten = Flatten()
        self.out = Dense(48, activation="linear")
        self.pump_station = pump_station
        self._input_shape = input_shape

    def get_config(self):
        """"
        :return config_dict needed to reconstruct this model
        """
        return {"pump_station": self.pump_station, "input_shape": self._input_shape}

    def call(self, inputs, training=None, mask=None):
        """"
        Does a forward pass over the model
        """
        x = self.conv_1(inputs)
        x = self.conv_2(x)
        x = self.conv_3(x)
        x = self.flatten(x)
        return self.out(x)
