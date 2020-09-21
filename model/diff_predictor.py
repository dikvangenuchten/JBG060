import os
import tensorflow as tf


class DiffPredictor(tf.keras.Model):
    def __init__(self, pump_station):
        super().__init__()
        self.pump_station = pump_station

    def build(self, input_shape):
        pass

    def __call__(self, *args, **kwargs):
        pass

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
