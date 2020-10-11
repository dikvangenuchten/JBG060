import numpy as np
from digital_twin.pump import Pump
import bayes_opt


class SewageSystem:
    def __init__(self, pumps):
        self.pumps: {str: Pump} = {pump.name: pump for pump in pumps}
        self.flow = 0
        self.max_flow_deviation = 0.1
        self.max_level = 7
        self.target_level = 1
        self.look_ahead = 24
        self.discount_factor = 0.90
        self.total_outflow_handled = 0

    def step(self, pump_step_data: dict):
        """"
        Calculates the (approximate) optimal pumping scenario for each pump
        and updates statistics on how it is doing
        """
        for pump, model_input, actual_level in pump_step_data.items():
            pump.pre_step(model_input, actual_level)

        bounds = {}
        for pump in self.pumps.values():
            pump_bounds = {pump.name + "_" + str(i): (0.55, 1) for i in range(self.look_ahead)}
            bounds.update(pump_bounds)

        optimizer = bayes_opt.bayesian_optimization.BayesianOptimization(
            f=self.optimization_func,
            pbounds=bounds
        )

        optimizer.maximize()
        optimal_packed_dict = optimizer.max()
        optimal_pumps_speeds = self.dict_unpacker(optimal_packed_dict)

        total_step_outflow = 0
        for pump, optimal_speeds in optimal_pumps_speeds.items():
            total_step_outflow += self.pumps[pump].post_step(optimal_speeds)

        self.total_outflow_handled += total_step_outflow

    def optimization_func(self, packed_dict):
        """
        Cost function to optimize for the bayesian optimization
        :param packed_dict:
        :return: float the penalty occuered from this pumping scenario
        """
        pump_speeds = self.dict_unpacker(packed_dict)
        pump_cost = 0
        all_flows = np.zeros(self.look_ahead)
        for pump, speed in pump_speeds.items():
            cost, flows = self.pumps[pump].simulate_pump_speeds(pump_speeds=speed)
            all_flows += flows
            pump_cost += cost

        smooth_cost = 0
        perc_diffs = np.diff(all_flows) / all_flows[:-1] * 100
        for i, perc_diff in enumerate(perc_diffs):
            smooth_cost += perc_diffs * self.discount_factor ** i

        return -(pump_cost + smooth_cost)

    def dict_unpacker(self, packed_dict: {str: float}):
        """"
        unpacks the dict needed in the bayesian optimization function to a useable dict
        """
        unpacked_dict = {}
        for key, value in packed_dict.items():
            pump_name, t = key.split(sep="_")
            speeds = unpacked_dict.get(pump_name, np.zeros(shape=self.look_ahead))
            speeds[t] = value
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


if __name__ == '__main__':
    pass
