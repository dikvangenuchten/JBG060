""""
Various util functions for the digital twin
"""
import math
import os
from typing import Tuple
from itertools import zip_longest

import numpy as np
import tensorflow as tf

from preprocessing.data_handler import DataHandler
from model.diff_predictor import DiffPredictor
from digital_twin.pump import Pump


def initiate_pump(models_dir: str, pump_name: str, data_handler: DataHandler, t: int) -> Pump:
    """
    Creates a pump, based on the state at time step t
    :param models_dir: The directory where the trained models are saved, or should be saved if none trained yet
    :param pump_name: The name of this pumping station
    :param data_handler: The data handler for this pump
    :param t: The time step from which the level needs to be measured
    :return pump: The initiated Pump
    """
    dry_pump_model = load_model(models_dir=models_dir, pump_name=pump_name, dry=True, wet=False)
    wet_pump_model = load_model(models_dir=models_dir, pump_name=pump_name, dry=False, wet=True)

    min_capacity, max_capacity, max_pump_flow, start_volume = data_handler.get_initiate_data(t)
    return Pump(
        name=pump_name,
        min_capacity=min_capacity,
        max_capacity=max_capacity,
        max_pump_flow=max_pump_flow,
        start_volume=start_volume,
        dry_model=dry_pump_model,
        wet_model=wet_pump_model
    )


def load_model(models_dir: str, pump_name: str, dry: bool, wet: bool) -> tf.keras.Model:
    """
    :param models_dir:
    :param pump_name:
    :return: the keras model trained for this pumping stations
    """
    if dry and not wet:
        model_type = "dry_only"
    elif not dry and wet:
        model_type = "wet_only"
    else:
        model_type = "dry_and_wet"
    save_dir = os.path.join(models_dir, pump_name, model_type)
    path = os.path.join(models_dir, pump_name, model_type, f"trained_model")
    try:
        model = tf.keras.models.load_model(filepath=path)
    except IOError as e:
        print(f"Trained model not available for {pump_name}, training from scratch")
        model = train(save_dir=save_dir, pump_name=pump_name, dry=dry, wet=wet)
    return model


def train(save_dir: str, pump_name: str, dry, wet) -> tf.keras.Model:
    """
    Trains a model based on the pump name
    """
    data_handler = load_train_data(pump_name=pump_name)
    model = create_model(pump_name=pump_name, data_handler=data_handler)
    train_model(epochs=10, data_handler=data_handler, model=model, save_dir=save_dir,
                dry_days=dry, wet_days=wet)
    return model


def load_train_data(pump_name) -> DataHandler:
    """
    Loads a data handler for the specified pump
    Requires the data to be in the folder processed/*
    And the csv for this pump to be named: {pump_name}.csv
    """
    data_handler = DataHandler(pump_station_name=pump_name,
                               actual_rainfall_path=os.path.join("processed",
                                                                 "data_rainfall_rain_timeseries_Download__.csv"),
                               predicted_rainfall_path=os.path.join("processed", "rainfallpredictionsHourlyV3.csv"),
                               in_flow_path=os.path.join("processed", f"pump_in_flow_appr_{pump_name}.csv"))
    data_handler.load_data()
    return data_handler


def create_model(pump_name: str, data_handler: DataHandler) -> tf.keras.Model:
    """
    Creates a keras model
    :return model: the untrained but compiled model
    """
    model = DiffPredictor(pump_name, input_shape=data_handler.x_shape)
    model.build(data_handler.x_shape)
    model.summary()
    model.compile(
        optimizer="adam",
        loss="mae",
        metrics=["mse", "mae"],
        run_eagerly=False
    )
    model.summary()
    return model


def train_model(epochs: int, data_handler: DataHandler, model: tf.keras.Model, save_dir: str,
                batch_size: int = 64, loss_weights: dict = None,
                dry_days=True, wet_days=False) -> tf.keras.Model:
    """"
    Trains a model, and saves it to cwd/models_dir/model_name/model_type/trained_model
    To be loaded by
    """
    for epoch in range(epochs):
        print(f"Starting Epoch {epoch}")
        train_data = data_handler.train_iterator(batch_size=batch_size, dry_days=dry_days, wet_days=wet_days)
        model.fit(train_data, class_weight=loss_weights)
        print(f"Finished training on Epoch {epoch}")
        test_data = data_handler.test_iterator(batch_size=batch_size, dry_days=dry_days, wet_days=wet_days)
        model.evaluate(test_data)
        # x_data, y_true = data_handler[500]
        # y_pred = model.predict(tf.expand_dims(x_data, axis=0))[0]
        # print(f"Model: \n"
        #       f"Differences: {y_true - y_pred}\n"
        #       f"Predictions: {y_pred} \n"
        #       f"True labels: {y_true}")
        print(f"Finished evaluation on Epoch {epoch}")
        model.save(os.path.join(save_dir, "checkpoints", str(epoch)))
    model.save(os.path.join(save_dir, "trained_model"))
    return model


def get_test_train_on_inflow(inflow=None, dry_days: bool = True, wet_days: bool = False):
    train_ts = []
    test_ts = []

    ts = t_calculator(df=inflow, time_col_name="index")
    first_t = ts.min()
    last_t = ts.max()
    if dry_days and wet_days:
        all_ts = ts
    elif dry_days:
        all_ts = ts[inflow < 2 * inflow.mean()]
        pass
    elif wet_days:
        all_ts = ts[inflow > 1.5 * inflow.mean()]
    else:
        raise ValueError("Invalid values")

    # Skip first and last days as they are needed as buffer for the predictions
    all_ts = all_ts[first_t + 50 < all_ts]
    all_ts = all_ts[all_ts < last_t - 50]
    for subset_ts in grouper(all_ts, 24 * 7 * 10):
        train_ts += subset_ts[:math.floor(len(subset_ts) * 0.8)]
        test_ts += subset_ts[math.ceil(len(subset_ts) * 0.8):]
    train_ts = list(filter(None, train_ts))
    test_ts = list(filter(None, test_ts))
    return train_ts, test_ts


def get_test_train_on_rain(rainfall_data=None, dry_days: bool = True, wet_days: bool = False):
    train_ts = []
    test_ts = []

    t_calculator(df=rainfall_data, time_col_name="Begin")
    first_t = rainfall_data["t"].min()
    last_t = rainfall_data["t"].max()
    if dry_days and wet_days:
        all_ts = rainfall_data["t"]
    elif dry_days:
        rainfall_data = rainfall_data[rainfall_data["Total Rainfall"] < 0.35]
        all_ts = rainfall_data["t"]
        pass
    elif wet_days:
        rainfall_data = rainfall_data[rainfall_data["Total Rainfall"] >= 0.25]
        all_ts = rainfall_data["t"]
    else:
        raise ValueError("Invalid values")

    # Skip first and last days as they are needed as buffer for the predictions
    all_ts = all_ts[first_t + 50 < all_ts]
    all_ts = all_ts[all_ts < last_t - 50]
    for subset_ts in grouper(all_ts, 24 * 7 * 10):
        train_ts += subset_ts[:math.floor(len(subset_ts) * 0.8)]
        test_ts += subset_ts[math.ceil(len(subset_ts) * 0.8):]
    train_ts = list(filter(None, train_ts))
    test_ts = list(filter(None, test_ts))
    return train_ts, test_ts


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def dry_wet_days(df):
    """
    Makes df for dry and wet days, need to make rainbuckets first
    """

    dry_days = df[df['daily_rain_none']]
    wet_days = df[df['daily_rain_none']]

    return dry_days, wet_days


def t_calculator(df, time_col_name: str, start_time: str = '2018-01-01 00:00:00'):
    """
    Adds a column to the data frame df with the difference in hours to the given start time and the time of an item
    in the df
    """

    import pandas as pd
    if time_col_name == "index":
        t = (df.index - pd.to_datetime(start_time, format='%Y-%m-%d %H:%M:%S')).astype('timedelta64[h]')

    else:
        t = (df[time_col_name] - pd.to_datetime(start_time, format='%Y-%m-%d %H:%M:%S')).astype('timedelta64[h]')
        df["t"] = t
    return t


def prepare_data(data_handler: DataHandler, t: int) -> Tuple[np.ndarray, float]:
    """"
    Gets the data for a pump at time step t
    :returns
        model_input: nd.array, for the input of the model
        actual_inflow: float, the level at t
    """
    return data_handler.get_x_data(t), data_handler.get_y_data(t)
