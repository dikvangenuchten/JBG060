import math
import os

import numpy as np
import tensorflow as tf
import csv


class Pump:
    """
    Class for pumps
    """

    def __init__(self, name, min_capacity, max_capacity, max_pump_flow, start_volume, dry_model, wet_model):
        """
        A pump needs to have a max capacity, max pump flow and a starting level and a model
        """

        self.pump_name = name
        self.min_capacity: float = min_capacity
        self.max_capacity: float = max_capacity
        self.max_pump_flow: float = max_pump_flow
        self.volume: np.ndarray = start_volume
        self.dry_model: tf.keras.Model = dry_model
        self.wet_model: tf.keras.Model = wet_model
        self.predicted_volume = start_volume
        self.flood: int = 0
        self.pump_changes: int = 0
        self.pump_mode = 'Off'
        self.dry_predicted_inflows = None
        self.wet_predicted_inflows = None
        self.ahead_planning: int = 24
        self.discount_factor = 0.9
        self.overflow_penalty = 10
        self.actual_inflow: float = np.nan
        self.actual_outflow: float = np.nan

    def __str__(self):
        """
        String representation of a model
        prints the level of a model and the predicted level
        """
        string = 'level: ' + str(self.volume) + ', predicted level: ' + str(self.predicted_volume)
        return string

    def pre_step(self, model_input):
        """"
        Updates internal values needed for deciding what to do this time step
        """
        self.dry_predicted_inflows = self.dry_model.predict(np.expand_dims(model_input, 0))[0]
        self.wet_predicted_inflows = self.wet_model.predict(np.expand_dims(model_input, 0))[0]

    def post_step(self, pump_speeds, actual_inflow):
        """
        Updates internal values based on action taken at this time step
        """
        actual_outflow, overflow = self._update_level(pump_speeds[0], incoming_water=actual_inflow)
        if overflow:
            print(f"OVERFLOW IN PUMP {self.pump_name}!")
        self.actual_inflow = actual_inflow
        self.actual_outflow = actual_outflow
        return actual_inflow, actual_outflow, self.volume, overflow

    def get_min_speeds(self):
        pass

    def simulate_pump_speeds(self, pump_speeds: np.ndarray):
        """
        Simulates the pump using the provide pump_speeds and internal level and prediction data
        :return float: the cost of this pump_speed pattern
        :return [float]: the outflows for each t
        """
        # Pump is off if speed is below 0.6
        pump_speeds[pump_speeds < 0.6] = 0
        outflows: np.ndarray = pump_speeds * self.max_pump_flow
        level = self.volume
        levels = np.zeros_like(pump_speeds)
        adjusted_outflows = outflows.copy()
        overflow_cost = 0
        level_cost = 0
        for i in range(len(pump_speeds)):
            adjusted_outflows[i] = min(level + self._inflow(i), outflows[i])
            level = level + self._inflow(i) - adjusted_outflows[i]
            if level >= self.max_capacity * 0.9:
                overflow_cost += (self.overflow_penalty * (self.discount_factor ** i))
            levels[i] = level
            level_cost += self.to_bucket(level) * self.discount_factor ** i
        print(overflow_cost, level_cost, adjusted_outflows)
        return overflow_cost, level_cost, adjusted_outflows

    def get_min_safe_speeds(self, delta_t):
        volume = self.volume
        min_pump_speeds = []
        for t in range(delta_t):
            volume += self.dry_predicted_inflows[t]
            overflow = min(0, self.max_capacity - volume)
            min_pump_speeds.append(overflow / self.max_pump_flow)

    def _update_level(self, pump_level, incoming_water):
        """
        updates level by calculating the amount of water pumped away and the incoming water
        :returns the amount of water pumped out
        """

        outflow = min(self.volume + incoming_water - self.min_capacity, pump_level * self.max_pump_flow)
        self.volume = self.volume + incoming_water - outflow

        if overflow := self.volume > self.max_capacity:
            self.volume = self.max_capacity
            self.flood += 1
        if self.volume < self.min_capacity:
            self.volume = self.min_capacity

        if self.pump_mode == "Off" and pump_level > 0:
            self.pump_mode = "On"
            self.pump_changes += 1

        if self.pump_mode == "On" and pump_level == 0:
            self.pump_mode = "Off"
            self.pump_changes += 1

        return outflow, overflow

    def _predict_level(self, pump_level):
        """
        DEPRECATED
        predicts the level for the next hours
        """
        DeprecationWarning("DEPRECATED")
        predicted_incoming_water = self.dry_model()[0]
        self.predicted_volume = self.volume + predicted_incoming_water - pump_level * self.max_pump_flow

        if self.predicted_volume > self.max_capacity:
            self.predicted_volume = self.max_capacity
            print('Predicted Overflow!')  # Probably needs to be changed to something else
        if self.predicted_volume < self.min_capacity:
            self.predicted_volume = self.min_capacity

    def _inflow(self, delta_t):
        """"
        :returns the predicted inflow at t
        """
        assert 0 <= delta_t < len(self.dry_predicted_inflows), "That time step does not have a prediction yet"
        return self.dry_predicted_inflows[delta_t]

    def max_predicted_level(self, delta_t):
        """"
        DEPRECATED
        Calculates the maximum level this pump is expected to have at t + delta_t, assuming no pumping
        """
        DeprecationWarning("DEPRECATED")
        if delta_t <= 0:
            return self.volume
        else:
            return self.max_predicted_level(delta_t - 1) + self._inflow(delta_t)

    def min_predicted_level(self, delta_t):
        """"
        DEPRECATED
        Calculates the minimum level this pump can have at to have at t + delta_t, assuming max pumping
        """
        DeprecationWarning("DEPRECATED")
        if delta_t <= 0:
            return self.volume
        else:
            return max(self.min_capacity,
                       self.min_predicted_level(delta_t - 1) + self._inflow(delta_t) - self.max_pump_flow)

    def get_bucket(self):
        """
        returns the level of the data rounded to the closed 10
        """
        return self.to_bucket(self.volume)

    def to_bucket(self, level):
        """"
        Calculates what bucket this level belongs to
        """
        return math.ceil((level / self.max_capacity) * 10)

    def pumped_water(self, pump_level):
        """
        returns the amount of pumped water
        """

        pumped = pump_level * self.max_pump_flow

        if pumped > (self.volume - self.min_capacity):
            pumped = self.volume - self.min_capacity
        return pumped

    def save_data(self, t, directory):
        """
        save this classes data to a file
        """
        filename = os.path.join(directory, self.pump_name)

        # writes column names if file does not exist yet
        if not os.path.isfile(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(f'{filename}.csv', 'a', newline='') as writable_file:
                csv.writer(writable_file).writerow(
                    ["Time", "Level", "Predicted Wet Inflow", "Predicted Dry Inflow", "Actual Inflow", "Actual Outflow"]
                )

        # append a row whenever function is called
        with open(f'{filename}.csv', 'a', newline='') as writable_file:
            csv.writer(writable_file).writerow(
                [t, self.volume, self.wet_predicted_inflows[0], self.dry_predicted_inflows[0], self.actual_inflow,
                 self.actual_outflow]
            )
            print(f"pump: {self.pump_name}\n"
                  f"predicted inflow: {self.dry_predicted_inflows[0]}\n"
                  f"actual inflow   : {self.actual_inflow}\n"
                  f"actual outflow  : {self.actual_outflow}")
