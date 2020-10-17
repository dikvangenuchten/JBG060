""""
Various util functions for the digital twin
"""
import os
from typing import Tuple

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
    pump_model = load_model(models_dir=models_dir, pump_name=pump_name)
    min_capacity, max_capacity, start_level, max_pump_flow = data_handler.get_initiate_data(t)
    return Pump(name=pump_name,
                min_capacity=min_capacity,
                max_capacity=max_capacity,
                max_pump_flow=max_pump_flow,
                start_level=start_level,
                model=pump_model
                )


def load_model(models_dir: str, pump_name: str) -> tf.keras.Model:
    """
    :param models_dir:
    :param pump_name:
    :return: the keras model trained for this pumping stations
    """
    path = os.path.join(models_dir, pump_name, "trained_model")
    try:
        model = tf.keras.models.load_model(filepath=path)
    except IOError as e:
        print(f"Trained model not available for {pump_name}, training from scratch")
        model = train(models_dir=models_dir, pump_name=pump_name)
    return model


def train(models_dir: str, pump_name: str) -> tf.keras.Model:
    """
    Trains a model based on the pump name
    """
    data_handler = load_train_data(pump_name=pump_name)
    model = create_model(pump_name=pump_name, data_handler=data_handler)
    train_model(epochs=10, data_handler=data_handler, model=model, models_dir=models_dir, model_name=pump_name)
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
        optimizer="rmsprop",
        loss="mse",
        metrics=["mse", "mae"],
        run_eagerly=False
    )
    return model


def train_model(epochs: int, data_handler: DataHandler, model: tf.keras.Model, models_dir: str,
                model_name: str = "unnamed",
                batch_size: int = 64, loss_weights: dict = None) -> tf.keras.Model:
    """"
    Trains a model, and saves it to cwd/models_dir/model_name/trained_model
    To be loaded by
    """
    for epoch in range(epochs):
        print(f"Starting Epoch {epoch}")
        train_data = data_handler.train_iterator(batch_size=batch_size)
        model.fit(train_data, class_weight=loss_weights)
        print(f"Finished training on Epoch {epoch}")
        test_data = data_handler.test_iterator(batch_size=batch_size)
        model.evaluate(test_data)
        print(f"Finished evaluation on Epoch {epoch}")
        model.save(os.path.join(models_dir, model_name, "checkpoints", str(epoch)))
    model.save(os.path.join(models_dir, model_name, "trained_model"))
    return model


def dry_wet_days(df):
    """
    Makes df for dry and wet days, need to make rainbuckets first
    """

    dry_days = df[df['daily_rain_none'] == 1]
    wet_days = df[df['daily_rain_none'] == 0]

    return dry_days, wet_days


def t_calculator(df, time_col_name: str, start_time: str = '2018-01-01 00:00:00'):
    """
    Adds a column to the data frame df with the difference in hours to the given start time and the time of an item
    in the df
    """

    from datetime import datetime

    time_list = df[time_col_name].values.tolist()
    datetime_list = []
    for date in time_list:
        datetime_list.append(int((datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                                  - datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600))
    df['t'] = datetime_list


def prepare_data(data_handler: DataHandler, t: int) -> Tuple[np.ndarray, float]:
    """"
    Gets the data for a pump at time step t
    :returns
        model_input: nd.array, for the input of the model
        actual_inflow: float, the level at t
    """
    return data_handler.get_x_data(t), data_handler.get_y_data(t)
