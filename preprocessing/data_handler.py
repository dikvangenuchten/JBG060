import os
import pandas as pd
import numpy as np
import pandas as pd


class DataHandler:
    def __init__(self, pump_station_name: str,
                 actual_rainfall_path: str = "processed/data_rainfall_rain_timeseries_Download__.csv",
                 predicted_rainfall_path: str = "processed/rainfallpredictionsHourlyV3.csv",
                 flow_path: str = os.path.join('preprocessing', 'processed', 'helftheuvel_1hour.csv')):
        self.actual_rainfall_path = actual_rainfall_path
        self.predicted_rainfall_path = predicted_rainfall_path
        self.pump_station_name = pump_station_name
        self.actual_rainfall_data = pd.read_csv(self.actual_rainfall_path)
        self.predicted_rainfall_data = pd.read_csv(self.predicted_rainfall_path)

        print(self.actual_rainfall_data)

        self.flow_path = flow_path
        self.flow_df = None
        self.x_shape = (1, 48)

    def load_data(self):
        """"
        Loads the data into memory
        """
        if self.flow_path is not None:
            self.flow_df = pd.read_csv(self.flow_path, index_col=0).iloc[:, 0]

        train_test_split = round(len(self.flow_df) * 0.5)
        train_data = self.iterator(self.flow_df.index[:train_test_split])
        test_data = self.iterator(self.flow_df.index[train_test_split:])
        return train_data, test_data

    def iterator(self, dates):
        """
        Iterates of the given dates (as index) and returns the data from those dates
        :param dates:
        :return: data from __getitem__
        """
        for date in dates:
            yield self.__getitem__(date)

    def __getitem__(self, index: int):
        """"
        Returns the information present on index
        Index 48 will return the data as an array
        with e.g. the actual rain of hours 0 to 48
        and the predicted rain of hours 48 to 96
        """
        return np.array(self._get_flow(index))

    def _get_flow(self, t, delta=48):
        """
        Returns the flow between t and t+48 were t=0 is the beginning of the dataset, being 2018-01-01 00:00
        :param t: int, is the index from which point we want to get the data from
        :param delta: int, the amount of rows after t we want to get the data from
        """
        return self.flow_df[t:t + delta]

    def _get_rainfall_prediction(self, t, duration):
        pass
