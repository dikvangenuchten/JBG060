""""
Various util functions for the digital twin
"""
import os

import tensorflow as tf

from preprocessing.data_handler import DataHandler
from model.diff_predictor import DiffPredictor
from digital_twin.pump import Pump


def initiate_pump(models_dir: str, pump_name: str, t: int) -> Pump:
    """
    Creates a pump, based on the state at time step t
    :param models_dir: The directory where the trained models are saved, or should be saved if none trained yet
    :param pump_name: The name of this pumping station
    :param t: The timestep from which the level needs to be measured
    :return pump: The initated Pump
    """
    pump_model = load_model(models_dir=models_dir, pump_name=pump_name)
    # TODO get pump statistics (max/min capacity, max flow)
    # TODO get pump level at t
    return Pump(name=pump_name,
                min_capacity=None,
                max_capacity=None,
                max_pump_flow=None,
                start_level=None,
                model=pump_model, )


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
    model = create_model(data_handler=data_handler)
    train_model(epochs=10, data_handler=data_handler, model=model, models_dir="trained_models", model_name=pump_name)
    return model


def load_train_data(pump_name) -> DataHandler:
    """
    Loads a data handler for the specified pump
    Requires the data to be in the folder processed/*
    And the csv for this pump to be named: {pump_name}.csv
    """
    return DataHandler(pump_station_name=pump_name,
                       actual_rainfall_path=os.path.join("processed", "data_rainfall_rain_timeseries_Download__.csv"),
                       predicted_rainfall_path=os.path.join("processed", "rainfallpredictionsHourlyV3.csv"),
                       flow_path=os.path.join("processed", pump_name + ".csv"))


def create_model(data_handler: DataHandler) -> tf.keras.Model:
    """
    Creates a keras model
    :return model: the untrained but compiled model
    """
    model = DiffPredictor("helftheuvel", input_shape=data_handler.x_shape)
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


def dry_wet_days(df):
    """
    Makes df for dry and wet days, need to make rainbuckets first
    """

    dry_days = df[df['daily_rain_none'] == 1]
    wet_days = df[df['daily_rain_none'] == 0]

    return dry_days, wet_days


def t_calculator(df, time_col_name: str, start_time: str = '2018-01-01 00:00:00'):
    """
    Adds a column to the dataframe df with the difference in hours to the given start time and the time of an item
    in the df
    """

    from datetime import datetime

    time_list = df[time_col_name].values.tolist()
    datetime_list = []
    for date in time_list:
        datetime_list.append(int((datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                                  - datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600))
    df['t'] = datetime_list
