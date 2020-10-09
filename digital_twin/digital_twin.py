from typing import Tuple

import numpy as np
import tensorflow as tf
from digital_twin.pump_class import Pump
from digital_twin.sewage_system import SewageSystem


def load_model(pump_name) -> tf.keras.Model:
    """
    :param pump_name:
    :return: the keras model trained for this pumping stations
    """

    # TODO check if there is a trained model for this pump
    # TODO load model trained for this pump or train model for this pump


def train_model(pump_name) -> tf.keras.Model:
    """
    Trains a model based on the pump name
    """

    # TODO load data for pump
    # TODO Train model on data
    # TODO Test model on train data


def initiate_pump(pump_name, t) -> Pump:
    """
    Creates a pump, based on the state at time step t
    :param pump_name:
    :param t:
    :return:
    """

    # TODO get pump statistics (max/min capacity, max flow)
    # TODO get pump level at t
    # TODO load model
    # TODO Initiate and return pump


def prepare_data(pump_name, t) -> Tuple[np.ndarray, float]:
    """"
    Gets the data for pump_name. e.g. helftheuvel at timestep t
    :returns
        model_input: nd.array, for the input of the model
        actual_inflow: float, the level at t
    """

    # TODO load the data needed for a step
    # TODO preprocess if necessary


pump_names = [
    "haarsteeg"
]
start_t = 100
end_t = 1000

if __name__ == '__main__':

    pumps = [initiate_pump(pump_name=pump_name, t=start_t) for pump_name in pump_names]
    sewage_system = SewageSystem(pumps)

    for time_step in range(start=start_t, stop=end_t, step=1):
        step_data = {pump_name: prepare_data(pump_name, time_step) for pump_name in pump_names}
        sewage_system.step(step_data)

    # TODO print evaluation of run
