from typing import Tuple

import numpy as np
from digital_twin.sewage_system import SewageSystem

from digital_twin.utils import initiate_pump


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
models_dir = "trained_models"
start_t = 100
end_t = 1000

if __name__ == '__main__':

    pumps = [initiate_pump(models_dir=models_dir, pump_name=pump_name, t=start_t) for pump_name in pump_names]
    sewage_system = SewageSystem(pumps)

    for time_step in range(start=start_t, stop=end_t, step=1):
        step_data = {pump_name: prepare_data(pump_name, time_step) for pump_name in pump_names}
        sewage_system.step(step_data)

    # TODO print evaluation of run
