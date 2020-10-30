import os
import argparse

import tensorflow as tf
import numpy as np
import pandas as pd

from preprocessing import concatenate_and_generate_overview
from preprocessing import unzipify
from preprocessing.data_handler import DataHandler
from model.diff_predictor import DiffPredictor
from validation.dry_wet_validation import DryWetValidation

data_path = "data"
model_dir = "saved_model"
epochs = 6
batch_size = 64
loss_weights = {i: x for i, x in enumerate(np.linspace(start=1, stop=0.5, num=48, endpoint=False, dtype=int))}

def train(epochs: int, data_handler: DataHandler, model: tf.keras.Model, models_dir: str, model_name: str = "unnamed",
          batch_size: int = 64, loss_weights: dict = None):
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
    data_handler.load_data()

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

    validator = None
    for x_data, y_data in data_handler.validation_iterator(start=0, end=2000):
        if not validator:
            validator = DryWetValidation(1000, y_data)
        prediction = model.predict(x_data)
        validator.step(prediction, y_data)

    best_val_df = None
    best_val_error = 99999
    for offset in np.arange(start=0, stop=2000, step=24):
        val_data = data_handler.validation_iterator(offset + 168, offset + 336)
        outs = []
        for x, y_true in val_data:
            y_pred = model.predict(x)
            out = {f"y_pred t+{i}": y_pred[0][i] for i in range(len(y_pred[0]))}
            out.update({f"error t+{i}": y_true[0][i] - y_pred[0][i] for i in range(len(y_true[0]))})
            out.update({"y_true": y_true[0][0]})
            outs.append(out)
        val_df = pd.DataFrame(data=outs)
        # print(val_df["error"].abs().sum())
        for i in range(48):
            if (abs_error := val_df[f"error t+{i}"].abs().sum()) < best_val_error:
                best_val_error = abs_error
                best_val_df = val_df
                val_df.to_csv("model_predictions.csv")
            print(abs_error)
    # TODO visualize outs
    best_val_df.to_csv("model_predictions.csv")
