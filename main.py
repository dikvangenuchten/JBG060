import os
import argparse

import tensorflow as tf
import numpy as np
import pandas as pd

from preprocessing import concatenate_and_generate_overview
from preprocessing import unzipify
from preprocessing.data_handler import DataHandler
from model.diff_predictor import DiffPredictor

data_path = "data"
model_dir = "saved_model"
epochs = 3
batch_size = 64
loss_weights = {i: x for i, x in enumerate(np.linspace(start=1, stop=0.5, num=48, endpoint=False, dtype=int))}
print(loss_weights)


def train(epochs: int, data_handler: DataHandler, model: tf.keras.Model, models_dir: str, model_name: str = "unnamed"):
    for epoch in range(epochs):
        print(f"Starting Epoch {epoch}")
        train_data = data_handler.train_iterator(batch_size=batch_size)
        model.fit(train_data, class_weight=loss_weights)
        print(f"Finished training on Epoch {epoch}")
        test_data = data_handler.test_iterator(batch_size=batch_size)
        model.evaluate(test_data)
        print(f"Finished evaluation on Epoch {epoch}")
        model.save(os.path.join(models_dir, model_name, "checkpoints", str(epoch)))
    model.save(os.path.join(model_name, model_name, "final_model"))


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

    train(epochs=epochs, data_handler=data_handler, model=model, models_dir=model_dir, model_name="helftheuvel")

    val_data = data_handler.validation_iterator(168, 336)
    outs = []
    for x, y_true in val_data:
        y_pred = model.predict(x)
        out = {f"y_pred t+{i}": y_true[0][i] for i in range(len(y_true[0]))}
        out.update({"y_true": y_true[0][0]})
        outs.append(out)
    val_df = pd.DataFrame(data=outs)
    val_df.to_csv("model_predictions.csv")
    print(val_df)
    print(val_df.describe())
    # TODO visualize outs
