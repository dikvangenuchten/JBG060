from digital_twin.sewage_system import SewageSystem

from digital_twin.utils import initiate_pump, load_train_data, prepare_data

pump_names = [
    "Helftheuvel"
]
models_dir = "trained_models"
start_t = 100
end_t = 1000

data_save_dir = "smart_sewage_sim_1"

if __name__ == '__main__':
    # Load the data
    data_handlers = {pump_name: load_train_data(pump_name) for pump_name in pump_names}

    # Load or create the pumps based on name and save location, and initiate them with the correct starting values
    pumps = [initiate_pump(data_handler=data_handlers[pump_name], models_dir=models_dir, pump_name=pump_name, t=start_t)
             for pump_name in pump_names]

    # Initiate the sewage system and assign pumps to it
    sewage_system = SewageSystem(pumps)

    for time_step in range(start_t, end_t, 1):
        model_data = {pump_name: data_handlers.get(pump_name).get_x_data(time_step) for pump_name in pump_names}
        inflow_data = {pump_name: data_handlers.get(pump_name).get_y_data(time_step)[0] for pump_name in pump_names}
        sewage_system.step(model_data, inflow_data)
        sewage_system.save_data(t=time_step, directory=data_save_dir)

    # TODO run plotter/print evaluation summary
