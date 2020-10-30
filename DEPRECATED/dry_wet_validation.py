import numpy as np


class DryWetValidation:
    def __init__(self, overflow_level, start_level):
        self.overflow_level = overflow_level
        self.current_level = start_level
        self.predicted_level = start_level
        self.errors = []

    def reset(self, start_level):
        self.current_level = start_level
        self.predicted_level = start_level

    def step(self, model_prediction, actual_diff):
        self.current_level = np.append(self.current_level, actual_diff)
        self.predicted_level = np.append(self.predicted_level, model_prediction)

    def results(self):
        pass