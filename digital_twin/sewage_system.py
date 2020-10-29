import os
import time
import csv
import numpy as np
from digital_twin.pump import Pump
import bayes_opt


class SewageSystem:
    def __init__(self, pumps):
        self.pumps: {str: Pump} = {pump.pump_name: pump for pump in pumps}
        self.flow = 0
        self.max_flow_deviation = 0.1
        self.max_level = 7
        self.target_level = 1
        self.look_ahead = 6
        self.discount_factor = 0.90
        self.total_inflow = 0
        self.total_outflow = 0
        self.total_overflows = 0

        self.total_step_inflow = 0
        self.total_step_outflow = 0
        self.epsilon = 1e-8

        self.bounds = {}
        for pump_name in self.pumps.keys():
            pump_bounds = {pump_name + "_" + str(i): (0.55, 1) for i in range(self.look_ahead)}
            self.bounds.update(pump_bounds)

    def dumb_step(self, model_data: dict, inflow_data: dict, lookahead: bool):
        """
        Simulates the current system
        """
        for pump_name, model_input in model_data.items():
            self.pumps.get(pump_name).pre_step(model_input)

        total_step_inflow = 0
        total_step_outflow = 0
        total_step_level = 0
        total_step_overflows = 0
        for pump_name, inflow in inflow_data.items():
            pump = self.pumps[pump_name]
            mode = pump.pump_mode
            bucket = pump.get_bucket() if not lookahead else pump.get_predicted_bucket()
            if bucket > 4:
                mode = "On"
            elif bucket <= 2:
                mode = "Off"

            if mode == "On":
                inflow, outflow, level, overflow = pump.post_step(pump_speeds=[1], actual_inflow=inflow)
            else:
                inflow, outflow, level, overflow = pump.post_step(pump_speeds=[0], actual_inflow=inflow)
            total_step_inflow += inflow
            total_step_outflow += outflow
            total_step_level += level
            total_step_overflows += overflow

        self.total_outflow = total_step_outflow
        self.total_inflow = total_step_inflow

    def known_step(self, model_data: dict, inflow_data: dict):
        for pump_name, model_input in model_data.items():
            pass

    def step(self, model_data: dict, inflow_data: dict):
        """"
        Calculates the (approximate) optimal pumping scenario for each pump
        and updates statistics on how it is doing
        """
        for pump_name, model_input in model_data.items():
            self.pumps.get(pump_name).pre_step(model_input)
        try:
            optimizer = bayes_opt.bayesian_optimization.BayesianOptimization(
                f=self.optimization_func,
                pbounds=self.bounds,
                verbose=0,
            )
            start = time.time()
            print("Start optimize")
            optimizer.maximize(n_iter=15)
            print(f"Optimizing took: {time.time() - start}")
            optimal_packed_dict = optimizer.max
            optimal_params = optimal_packed_dict["params"]
            optimal_pumps_speeds = self.dict_unpacker(optimal_params)
            cost = optimal_packed_dict.get('target')
        except Exception as e:
            print(f"Exception {e}")
            optimal_pumps_speeds = np.ones(shape=(len(self.pumps), len(self.pumps)))
            cost = -100000

        step_stats = {pump_name: self.pumps[pump_name].post_step(optimal_speeds, inflow_data.get(pump_name))
                      for pump_name, optimal_speeds in optimal_pumps_speeds.items()}

        self.total_step_inflow = 0
        self.total_step_outflow = 0
        total_step_level = 0
        total_step_overflows = 0
        for inflow, outflow, level, overflow in step_stats.values():
            self.total_step_inflow += inflow
            self.total_step_outflow += outflow
            total_step_level += level
            total_step_overflows += overflow

        # print(f"Total Inflow: {total_step_inflow}, Total Outflow: {total_step_outflow}\n"
        #       f"Total Level: {total_step_level}, Total Overflows: {total_step_overflows}")
        self.total_outflow += self.total_step_outflow
        self.total_overflows += self.total_step_overflows
        return cost, self.total_step_outflow

    def optimization_func(self, **packed_dict):
        """
        Cost function to optimize for the bayesian optimization
        :param packed_dict:
        :return: float the penalty occuered from this pumping scenario
        """
        pump_speeds = self.dict_unpacker(packed_dict)
        pump_overflow_cost = 0
        pump_level_cost = 0
        all_flows = np.zeros(self.look_ahead)
        for pump, speed in pump_speeds.items():
            overflow_cost, level_cost, flows = self.pumps[pump].simulate_pump_speeds(pump_speeds=speed)
            all_flows += flows
            pump_overflow_cost += overflow_cost
            pump_level_cost += level_cost

        smooth_cost = 0
        perc_diffs = np.diff(all_flows) / (all_flows[:-1] + self.epsilon) * 100
        for i, perc_diff in enumerate(perc_diffs):
            smooth_cost += abs(perc_diff) * self.discount_factor ** i

        return -(pump_overflow_cost + 10 * smooth_cost + pump_level_cost)

    def dict_unpacker(self, packed_dict: {str: float}):
        """"
        unpacks the dict needed in the bayesian optimization function to a useable dict
        """
        unpacked_dict = {}
        for key, value in packed_dict.items():
            pump_name, t = key.split(sep="_")
            speeds = unpacked_dict.get(pump_name, np.zeros(shape=self.look_ahead))
            speeds[int(t)] = value
            unpacked_dict[pump_name] = speeds
        return unpacked_dict

    def get_min_max_flow(self, t):
        """"
        DEPRECATED
        Get the predicted flow and pumping speeds at time step t, where currently is always t=0
        """
        buckets = {pump.name: pump.get_bucket(t) for pump in self.pumps.values()}
        min_pump_speeds = {pump.name: 0 for pump in self.pumps.values()}
        min_flow = 0
        for pump, level_bucket in buckets.items():
            # When the pump is predicted to go over the max level, pump at full speed
            if level_bucket > self.max_level:
                min_pump_speeds[pump] = 1
                min_flow += pump.pumped_water(1)

        # Calculate what the max flow of all pumps above target level is
        max_flow = min_flow
        max_pump_speeds = min_pump_speeds.copy()
        for pump, level_bucket in buckets:
            if self.target_level < level_bucket < self.max_level:
                max_pump_speeds[pump] = 1
                max_flow += pump.pumped_water(1)

        return min_flow, min_pump_speeds, max_flow, max_pump_speeds

    def get_levels(self, t):
        """"
        DEPRECATED
        :return the bucket level of each pump
        """
        return {pump.name: pump.get_bucket(t) for pump in self.pumps.values()}

    def save_data(self, t, directory):
        """
        save this classes data to a file
        """
        filename = os.path.join(directory, "complete_sewage_system")

        # writes column names if file does not exist yet
        if not os.path.isfile(filename + ".csv"):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(f'{filename}.csv', 'a', newline='') as writable_file:
                csv.writer(writable_file).writerow(["Time", "Total Inflow", "Total Outflow"])

        # append a row whenever function is called
        with open(f'{filename}.csv', 'a', newline='') as writable_file:
            csv.writer(writable_file).writerow([t, self.total_step_inflow, self.total_step_outflow])

            # Also call each pump
        for pump in self.pumps.values():
            pump.save_data(t, directory)


if __name__ == '__main__':
    pass
