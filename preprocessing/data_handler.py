import os
import pandas as pd
import numpy as np
import pandas as pd


class DataHandler:
    def __init__(self, pump_station_name: str,
                 actual_rainfall_path: str = "processed/data_rainfall_rain_timeseries_Download__.csv",
                 predicted_rainfall_path: str = "processed/rainfallpredictionsHourlyV3.csv",
                 flow_path: str = os.path.join('processed', 'helftheuvel_1hour.csv')):
        self.actual_rainfall_path = actual_rainfall_path
        self.predicted_rainfall_path = predicted_rainfall_path
        self.pump_station_name = pump_station_name

        self.flow_path = flow_path
        self.flow_df = None
        # (batch, time, features)
        self.x_shape = (None, 48, 3)

    def load_data(self, batch_size=64):
        """"
        Loads the data into memory
        """
        if self.flow_path is not None:
            self.flow_df = pd.read_csv(self.flow_path, index_col=0)
            # Get hour of day as integer
            self.flow_df["time_hour"] = pd.to_datetime(self.flow_df.Date).dt.hour.astype(float)
            # Drop date
            self.flow_df.drop(columns="Date", inplace=True)

        if self.actual_rainfall_path is not None:
            self.actual_rainfall_data = pd.read_csv(self.actual_rainfall_path)

        if self.predicted_rainfall_path is not None:
            self.predicted_rainfall_data = pd.read_csv(self.predicted_rainfall_path)

        train_data = self.iterator(range(0, round(0.1 * len(self.flow_df))), batch_size=batch_size)
        test_data = self.iterator(range(round(0.9 * len(self.flow_df)), len(self.flow_df)), batch_size=batch_size)
        for i, train in enumerate(train_data):
            print(i, train)
            if i > 2:
                break
        return train_data, test_data

    def iterator(self, dates, batch_size):
        """
        Iterates of the given dates (as index) and returns the data from those dates
        :param dates:
        :return: data from __getitem__
        """
        for date in dates:
            x_train = np.expand_dims(self.__getitem__(date), [0])
            y_true = np.expand_dims(([1] * 48), 0)
            print(y_true)
            # TODO proper y data
            yield x_train, y_true

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

    def _get_rainfall_prediction(self, t, delta=48):
        pass
