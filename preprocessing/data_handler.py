import os
import numpy as np
import pandas as pd


class DataHandler:
    def __init__(self, pump_station_name: str,
                 actual_rainfall_path: str = "processed/data_rainfall_rain_timeseries_Download__.csv",
                 predicted_rainfall_path: str = "processed/rainfallpredictionsHourlyV3.csv",
                 flow_path: str = os.path.join('processed', 'helftheuvel_1hour.csv')):
        self.actual_rainfall_path = actual_rainfall_path

        self.predicted_rainfall_path = predicted_rainfall_path
        self.predicted_rainfall_data = None
        self.pump_station_name = pump_station_name

        self.flow_path = flow_path
        self.flow_df = None
        self.diff = None

        self.x_shape = None
        self.y_shape = None

    def load_data(self, batch_size=64):
        """"
        Loads the data into memory
        """
        if self.flow_path is not None:
            self.flow_df = pd.read_csv(self.flow_path, index_col=0)
            # Get hour of day as integer
            self.flow_df["time_hour"] = pd.to_datetime(self.flow_df.Date).dt.hour.astype(float)
            self.diff = self.flow_df.helftheuvelweg.diff()
            # Drop date
            self.flow_df.drop(columns="Date", inplace=True)

        if self.actual_rainfall_path is not None:
            self.actual_rainfall_data = pd.read_csv(self.actual_rainfall_path)

        if self.predicted_rainfall_path is not None:
            self.predicted_rainfall_data = pd.read_csv(self.predicted_rainfall_path)
            self.predicted_rainfall_data["time_hour"] = pd.to_datetime(
                self.predicted_rainfall_data.Time
            ).dt.hour.astype(float)
            self.predicted_rainfall_data = self.predicted_rainfall_data[self.predicted_rainfall_data.columns[3:7]]
        print(self.flow_df.describe())
        print(self.diff.describe())
        if self.x_shape is None:
            x, y = self.__getitem__(48)
            # Shape is (batch_size, time, features)
            self.x_shape = (None, *np.shape(x))
            self.y_shape = (None, *np.shape(y))

    def validation_iterator(self, start, end):
        return self.iterator(np.linspace(start=start, stop=end, num=end-start, dtype=np.int), batch_size=1)

    def train_iterator(self, batch_size):
        return self.iterator(range(48, round(0.8 * len(self.flow_df))), batch_size=batch_size)

    def test_iterator(self, batch_size):
        return self.iterator(range(round(0.9 * len(self.flow_df)), len(self.flow_df) - 48), batch_size=batch_size)

    def iterator(self, dates, batch_size):
        """
        Iterates of the given dates (as index) and returns the data from those dates
        :param dates:
        :return: data from __getitem__
        """
        _dates = [_date for _date in reversed(dates)]
        while len(_dates) != 0:
            x_train = []
            y_true = []
            for i in range(min(batch_size, len(_dates))):
                date = _dates.pop()
                x, y = self.__getitem__(date)
                x_train.append(x)
                y_true.append(y)
            x_train, y_true = np.array(x_train), np.array(y_true)
            yield x_train, y_true

    def __getitem__(self, index: int):
        """"
        Returns the information present on index
        Index 48 will return the data as an array
        with e.g. the actual rain of hours 0 to 48
        and the predicted rain of hours 48 to 96
        """

        x_data_flow = np.array(self._get_flow(index))
        x_data_rain = np.array(self._get_rainfall_prediction(index))
        x_data = np.concatenate([x_data_flow, x_data_rain], axis=1)
        y_data = np.array(self._get_diff(index))

        if np.any(np.isnan(x_data)):
            np.nan_to_num(x_data, copy=False)
        if np.any(np.isnan(y_data)):
            np.nan_to_num(y_data, copy=False)
        return x_data, y_data

    def _get_diff(self, t, delta=48):
        """"
        Returns the diff between t and t+delta
        diff_t = level_t - level_t-1
        with diff_0 = 0
        """
        return self.diff[t:t + delta]

    def _get_flow(self, t, delta=48):
        """
        Returns the flow between t-delta and t were t=0 is the beginning of the dataset, being 2018-01-01 00:00
        :param t: int, is the index from which point we want to get the data from
        :param delta: int, the amount of rows after t we want to get the data from
        :raise IndexOutOfRange error when delta is bigger then t
        """
        return self.flow_df[t:t+delta]

    def _get_rainfall_prediction(self, t, delta=48):
        """"
        Returns the rainfall prediction between t and t+48 were t=0 is the beginning of the dataset, being 2018-01-01
        """
        return self.predicted_rainfall_data[t:t + delta]
