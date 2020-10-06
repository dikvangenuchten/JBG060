import numpy as np


class SewageSystem:
    def __init__(self, pumps):
        self.pumps = pumps
        self.flow = 0
        self.max_flow_deviation = 0.1
        self.max_level = 7
        self.target_level = 1

    def get_speeds(self, delta):
        min_flows = []
        min_pump_speeds = []
        max_flows = []
        max_pump_speeds = []
        for t in delta:
            min_flow, min_pump_speed, max_flow, max_pump_speed = self.get_min_max_flow(t)
            min_flows.append(min_flow)
            min_pump_speeds.append(min_pump_speed)
            max_flows.append(max_flow)
            max_pump_speeds.append(max_pump_speed)
        # TODO minimize derivative over time, with hard the limitation of staying between min and max flow

    def get_min_max_flow(self, t):
        """"
        Get the predicted flow and pumping speeds at time step t, where currently is always t=0
        """
        buckets = [(pump, pump.get_bucket(t)) for pump in self.pumps]
        min_pump_speeds = {pump: 0 for pump in self.pumps}
        min_flow = 0
        for pump, level_bucket in buckets:
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
