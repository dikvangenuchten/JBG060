import math
import numpy as np
import tensorflow as tf


class Pump:
    """Class for pumps"""

    def __init__(self, name, min_capacity, max_capacity, max_pump_flow, start_level, model):
        """A pump needs to have a max capacity, max pump flow and a starting level and a model"""

        self.pump_name = name
        self.min_capacity: float = min_capacity
        self.max_capacity: float = max_capacity
        self.max_pump_flow: float = max_pump_flow
        self.level: np.ndarray = start_level
        self.model: tf.keras.Model = model
        self.predicted_level = start_level
        self.flood: int = 0
        self.pump_changes: int = 0
        self.pump_mode = 'Off'
        self.predicted_inflows = None
        self.ahead_planning: int = 24
        self.discount_factor = 0.9
        self.overflow_penalty = 10

    def __str__(self):
        """prints the level of a model and the predicted level"""

        string = 'level: ' + str(self.level) + ', predicted level: ' + str(self.predicted_level)
        return string

    def pre_step(self, model_input):
        """"
        Updates internal values needed for deciding what to do this time step
        """
        self.predicted_inflows = self.model.predict(np.expand_dims(model_input, 0))[0]

    def post_step(self, pump_speeds, actual_inflow):
        """
        Updates internal values based on action taken at this time step
        """
        return self._update_level(pump_speeds[0], incoming_water=actual_inflow)

    def simulate_pump_speeds(self, pump_speeds: np.ndarray):
        """
        Simulates the pump using the provide pump_speeds and internal level and prediction data
        :return float: the cost of this pump_speed pattern
        :return [float]: the outflows for each t
        """
        # Pump is off if speed is below 0.6
        pump_speeds[pump_speeds < 0.6] = 0
        outflows: np.ndarray = pump_speeds * self.max_pump_flow
        level = self.level
        levels = np.zeros_like(pump_speeds)
        adjusted_outflows = outflows.copy()
        cost = 0
        for i in range(len(pump_speeds)):
            adjusted_outflows[i] = min(level + self._inflow(i), outflows[i])
            level = level + self._inflow(i) - adjusted_outflows[i]
            if level >= self.max_capacity * 0.9:
                cost += (self.overflow_penalty * (self.discount_factor ** i))
            levels[i] = level
            cost += self.to_bucket(level) * self.discount_factor ** i

        return cost, adjusted_outflows

    def _update_level(self, pump_level, incoming_water):
        """
        updates level by calculating the amount of water pumped away and the incoming water
        :returns the amount of water pumped out
        """

        outflow = min(self.level + incoming_water - self.min_capacity, pump_level * self.max_pump_flow)
        self.level = self.level + incoming_water - outflow

        if self.level > self.max_capacity:
            self.level = self.max_capacity
            self.flood += 1
        if self.level < self.min_capacity:
            self.level = self.min_capacity

        if self.pump_mode == "Off" and pump_level > 0:
            self.pump_mode = "On"
            self.pump_changes += 1

        if self.pump_mode == "On" and pump_level == 0:
            self.pump_mode = "Off"
            self.pump_changes += 1

        return outflow

    def _predict_level(self, pump_level):
        """
        DEPRECATED
        predicts the level for the next hours
        """

        predicted_incoming_water = self.model()
        self.predicted_level = self.level + predicted_incoming_water - pump_level * self.max_pump_flow

        if self.predicted_level > self.max_capacity:
            self.predicted_level = self.max_capacity
            print('Predicted Overflow!')  # Probably needs to be changed to something else
        if self.predicted_level < self.min_capacity:
            self.predicted_level = self.min_capacity

    def _inflow(self, delta_t):
        """"
        :returns the predicted inflow at t
        """
        assert 0 <= delta_t < len(self.predicted_inflows), "That time step does not have a prediction yet"
        return self.predicted_inflows[delta_t]

    def max_predicted_level(self, delta_t):
        """"
        DEPRECATED
        Calculates the maximum level this pump is expected to have at t + delta_t, assuming no pumping
        """
        if delta_t <= 0:
            return self.level
        else:
            return self.max_predicted_level(delta_t - 1) + self._inflow(delta_t)

    def min_predicted_level(self, delta_t):
        """"
        DEPRECATED
        Calculates the minimum level this pump can have at to have at t + delta_t, assuming max pumping
        """
        if delta_t <= 0:
            return self.level
        else:
            return max(self.min_capacity,
                       self.min_predicted_level(delta_t - 1) + self._inflow(delta_t) - self.max_pump_flow)

    def get_bucket(self):
        """
        returns the level of the data rounded to the closed 10
        """
        return self.to_bucket(self.level)

    def to_bucket(self, level):
        """"
        Calculates what bucket this level belongs to
        """
        return math.ceil(level / self.max_capacity * 10) * 10

    def pumped_water(self, pump_level):
        """
        returns the amount of pumped water
        """

        pumped = pump_level * self.max_pump_flow

        if pumped > (self.level - self.min_capacity):
            pumped = self.level - self.min_capacity
        return pumped
