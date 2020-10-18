import os
import numpy as np
import pandas as pd
import tensorflow as tf


class DataHandler:
    def __init__(self, pump_station_name: str,
                 actual_rainfall_path: str = "processed/data_rainfall_rain_timeseries_Download__.csv",
                 predicted_rainfall_path: str = "processed/rainfallpredictionsHourlyV3.csv",
                 in_flow_path: str = os.path.join('processed', 'pump_in_flow_appr_Helftheuvel.csv')):
        self.actual_rainfall_path = actual_rainfall_path
        self.actual_rainfall_data = None

        self.predicted_rainfall_path = predicted_rainfall_path
        self.predicted_rainfall_data = None
        self.pump_station_name = pump_station_name

        self.max_level = None
        self.min_level = None
        self.pump_speed = None

        self.in_flow_path = in_flow_path
        self.inflow = None
        self.level = None

        self.x_shape = None
        self.y_shape = None

    def load_data(self):
        """"
        Loads the data into memory
        """
        print(self.pump_station_name)
        if self.in_flow_path is not None:
            in_flow_df = pd.read_csv(self.in_flow_path, index_col=0, parse_dates=True)
            # Get hour of day as integer
            print(self.in_flow_path)
            in_flow_df["flow_in"].replace(np.nan, 0, inplace=True)

            # in_flow_df["time_hour"] = pd.to_datetime(in_flow_df.index).hour.astype(int)
            self.inflow = in_flow_df.resample("H").flow_in.sum()
            # TODO fix naming in in_flow_df
            # TODO Change level to volume
            self.pump_speed = self.get_mean_fastest_pump_speed(in_flow_df.resample("H").sum())
            self.max_level = in_flow_df.iloc[:, 1].max()
            self.min_level = in_flow_df.iloc[:, 1].min()
            self.level = in_flow_df.iloc[:, 1].resample("H").max()

        if self.actual_rainfall_path is not None:
            self.actual_rainfall_data = pd.read_csv(self.actual_rainfall_path)

        if self.predicted_rainfall_path is not None:
            self.predicted_rainfall_data = pd.read_csv(self.predicted_rainfall_path)
            self.predicted_rainfall_data["time_hour"] = pd.to_datetime(
                self.predicted_rainfall_data.Time
            ).dt.hour.astype(float)
            self.predicted_rainfall_data = self.predicted_rainfall_data[self.predicted_rainfall_data.columns[3:7]]
            self.predicted_rainfall_data["time"] = self.predicted_rainfall_data.index % 24

        if self.x_shape is None:
            x, y = self.__getitem__(48)
            # Shape is (batch_size, time, features)
            self.x_shape = (None, *np.shape(x))
            self.y_shape = (None, *np.shape(y))

    def get_initiate_data(self, t):
        level_at_t = self.level[t]
        return self.min_level, self.max_level, self.pump_speed, level_at_t

    def level_to_volume(self, level):
        pass

    def validation_iterator(self, start, end):
        return self.iterator(np.linspace(start=start, stop=end, num=end - start, dtype=np.int), batch_size=1)

    def train_iterator(self, batch_size):
        return self.iterator(range(48, round(0.8 * len(self.inflow))), batch_size=batch_size)

    def test_iterator(self, batch_size):
        return self.iterator(range(round(0.9 * len(self.inflow)), len(self.inflow) - 48), batch_size=batch_size)

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
        return self.get_x_data(index), self.get_y_data(index)

    def get_x_data(self, t):
        """
        Returns the x data for time step t
        :param t: the time step for which the data is requested
        :return:
        """
        x_data = np.array(self._get_rainfall_prediction(t))
        if np.any(np.isnan(x_data)):
            np.nan_to_num(x_data, copy=False)
        return x_data

    def get_y_data(self, t):
        """
        Returns the y data for time step t
        :param t: the time step for which the data is requested
        :return:
        """
        y_data = np.array(self._get_diff(t))
        if np.any(np.isnan(y_data)):
            np.nan_to_num(y_data, copy=False)
        return y_data

    def get_level(self, t):
        """
        Returns the level of the pump at time step t
        :param t:
        :return:
        """
        return self.level[t]

    def _get_diff(self, t, delta=48):
        """"
        Returns the diff between t and t+delta
        diff_t = level_t - level_t-1
        with diff_0 = 0
        """
        return self.inflow[t:t + delta]

    def _get_rainfall_prediction(self, t, delta=48):
        """"
        Returns the rainfall prediction between t and t+48 were t=0 is the beginning of the dataset, being 2018-01-01
        """
        return self.predicted_rainfall_data[t:t + delta]

    @staticmethod
    def get_mean_fastest_pump_speed(full_df, nr_most_pumped=100):
        """
        Gets the mean of the most fastest times a pump has pumped while also removing outliers
        :param full_df: DataFrame, the pump dataframe with 'level_diff'
        :param nr_most_pumped: int, the amount of fastest hours we need to find the mean from
        """
        df = full_df.sort_values(by='hstWaarde', ascending=False).iloc[:nr_most_pumped]

        df['zscore'] = abs((df['hstWaarde'] - df['hstWaarde'].mean()) / df['hstWaarde'].std(ddof=0))

        df = df[df['zscore'] < 3]

        return abs(df['hstWaarde'].mean())
