import os
import argparse

import tensorflow as tf
import numpy as np

from preprocessing import concatenate_and_generate_overview
from preprocessing import unzipify
from preprocessing.data_handler import DataHandler
from model.diff_predictor import DiffPredictor

data_path = "data"
model_dir = "saved_model"
epochs = 10
batch_size = 64

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--unzipped', action='store_true', default=False,
                        help='whether we want to do an unzipify')
    parser.add_argument('-c', '--concat', action='store_true', default=False,
                        help='whether we want to do the concat')
    args = parser.parse_args()

    if args.unzipped:
        unzipify.search_and_unzip(data_path)
    if args.concat:
        concatenate_and_generate_overview.search_and_concat(data_path)

    data_handler = DataHandler(data_path)
    data_handler.load_data(batch_size=64)

    model = DiffPredictor("helftheuvel", input_shape=data_handler.x_shape)
    model.build(data_handler.x_shape)
    model.summary()
    model.compile(
        optimizer="rmsprop",
        loss="mse",
        metrics=["mse", "mae"],
        run_eagerly=False
    )

    for epoch in range(epochs):
        print(f"Starting Epoch {epoch}")
        train_data = data_handler.train_iterator(batch_size=batch_size)
        model.fit(train_data)
        print(f"Finished training on Epoch {epoch}")
        test_data = data_handler.test_iterator(batch_size=batch_size)
        model.evaluate(test_data)
        print(f"Finished evaluation on Epoch {epoch}")
        model.save(os.path.join(model_dir, "checkpoints", str(epoch)))

    # TODO Write proper validation tool

    model.save(model_dir)
