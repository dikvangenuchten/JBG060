import math


class Pump:
    '''Class for pumps'''

    def __init__(self, max_capacity, max_pump_flow, start_level, model):
        '''A pump needs to have a max capacity, max pump flow and a starting level and a model'''

        self.max_capacity = max_capacity
        self.max_pump_flow = max_pump_flow
        self.level = start_level
        self.model = model
        self.predicted_level = start_level

    def __str__(self):
        """prints the level of a model and the predicted level"""

        string = 'level: ' + str(self.level) + ', predicted level: ' + str(self.predicted_level)
        return string

    def update_level(self, pump_level, incoming_water):
        '''updates level by calculating the amount of water pumped away and the incoming water'''

        self.level = self.level + incoming_water - pump_level * self.max_pump_flow

        if self.level > self.max_capacity:
            self.level = self.max_capacity
            print('Overflow!')  # Probably needs to be changed to something else
        if self.level < 0:
            self.level = 0

    def predict_level(self, pump_level, predicted_incoming_water):
        """predicts the level for the next hours"""

        self.predicted_level = self.level + predicted_incoming_water - pump_level * self.max_pump_flow

        if self.predicted_level > self.max_capacity:
            self.predicted_level = self.max_capacity
            print('Predicted Overflow!')  # Probably needs to be changed to something else
        if self.predicted_level < 0:
            self.predicted_level = 0

    def get_bucket(self):
        '''returns the level of the data rounded to the closed 10'''

        bucket = math.ceil(self.level / self.max_capacity * 10) * 10
        return bucket

    def pumped_water(self, pump_level):
        '''returns the amount of pumped water'''

        pumped = pump_level * self.max_pump_flow

        if pumped > self.level:
            pumped = self.level
        return pumped
