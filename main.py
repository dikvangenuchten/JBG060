import os
import argparse

import tensorflow as tf

from preprocessing import concatenate_and_generate_overview
from preprocessing import unzipify
from preprocessing.data_handler import DataHandler
from model.diff_predictor import DiffPredictor

data_path = "data"
model_dir = "saved_model"
epochs = 10

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--unzipped', action='store_true', default=False,
                        help='whether we want to do an unzipify')
    parser.add_argument('-c', '--concat', action='store_true', default=False, help='whether we want to do the concat')
    parser.add_argument('-m', '--model', action='store_true', default=False, help='whether we want to run the model')
    args = parser.parse_args()

    if args.unzipped:
        unzipify.search_and_unzip(data_path)
    if args.concat:
        concatenate_and_generate_overview.search_and_concat(data_path)
    if args.model:
        data_handler = DataHandler(data_path)
        train_data, test_data = data_handler.load_data()

        model = DiffPredictor("pump_1")
        model.build(data_handler.x_shape)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(),
            loss=tf.keras.losses.MSE,
            metrics=[],
            run_eagerly=True
        )

        for epoch in range(epochs):
            print(f"Starting Epoch {epoch}")
            model.fit(train_data)
            print(f"Finished training on Epoch {epoch}")
            model.evaluate(test_data)
            print(f"Finished evaluation on Epoch {epoch}")
            model.save(os.path.join(model_dir, "checkpoints", str(epoch)))

        # TODO Write proper validation tool

        model.save(model_dir)
