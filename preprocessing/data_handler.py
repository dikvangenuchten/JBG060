import os
import numpy as np
import pandas as pd
import tensorflow as tf
import bisect

from digital_twin import utils


class DataHandler:
    def __init__(self, pump_station_name: str,
                 actual_rainfall_path: str = "processed/data_rainfall_rain_timeseries_Download__.csv",
                 predicted_rainfall_path: str = "processed/rainfallpredictionsHourlyV3.csv",
                 in_flow_path: str = os.path.join('processed', 'pump_in_flow_appr_Helftheuvel.csv'),
                 dry_days: bool = True, wet_days: bool = False, sample_time: str = "H"):
        self.actual_rainfall_path = actual_rainfall_path
        self.actual_rainfall_data = None

        self.predicted_rainfall_path = predicted_rainfall_path
        self.predicted_rainfall_data = None
        self.pump_station_name = pump_station_name

        self.volume = None
        self.max_volume = None
        self.min_volume = None
        self.max_level = None
        self.min_level = None
        self.pump_speed = None

        self.in_flow_path = in_flow_path
        self.inflow = None
        self.level = None

        self.x_shape = None
        self.y_shape = None

        self.dry_days = dry_days
        self.wet_days = wet_days
        self.train_ts = None
        self.test_ts = None

        self.sample_time = sample_time

    def load_data(self):
        """"
        Loads the data into memory
        """
        print(self.pump_station_name)
        if self.in_flow_path is not None:
            in_flow_df = pd.read_csv(self.in_flow_path, index_col=0, parse_dates=True)
            # Get hour of day as integer
            in_flow_df["flow_in"].replace(np.nan, 0, inplace=True)

            # in_flow_df["time_hour"] = pd.to_datetime(in_flow_df.index).hour.astype(int)
            self.inflow = in_flow_df.resample(self.sample_time).pad().flow_in.resample(self.sample_time).mean()
            # TODO fix naming in in_flow_df
            # TODO Change level to volume
            self.pump_speed = self.get_mean_fastest_pump_speed(in_flow_df.resample(self.sample_time).mean())
            self.volume = pd.read_csv(os.path.join("processed", f"{self.pump_station_name}_single_cm_m3.csv"),
                                      index_col=0)
            self.max_level = in_flow_df.iloc[:, 0].max()
            self.min_level = in_flow_df.iloc[:, 0].min()

            # 10 percent leeway to ensure the error is on the safe side
            self.max_volume = self.level_to_volume(self.max_level)
            self.min_volume = self.level_to_volume(self.min_level)

            # Resample the level data to hour, taking the maximum level during that hour
            self.level = in_flow_df.iloc[:, 1].resample(self.sample_time).max()

        if self.actual_rainfall_path is not None:
            actual_rainfall_data = pd.read_csv(self.actual_rainfall_path)
            time_data = actual_rainfall_data["Begin"]
            actual_rainfall_data.drop(columns=["Begin", "Eind", "Kwaliteit"])
            actual_rainfall_data = actual_rainfall_data.mean(axis=1)
            self.actual_rainfall_data = pd.concat(objs=[time_data, actual_rainfall_data], axis=1, ignore_index=True)
            self.actual_rainfall_data.columns = ["Begin", "Total Rainfall"]
            self.actual_rainfall_data["Begin"] = pd.to_datetime(self.actual_rainfall_data["Begin"])
            self.actual_rainfall_data = self.actual_rainfall_data.resample(self.sample_time, on="Begin").mean()
            self.actual_rainfall_data.reset_index(level=0, inplace=True)

        if self.predicted_rainfall_path is not None:
            self.predicted_rainfall_data = pd.read_csv(self.predicted_rainfall_path)
            self.predicted_rainfall_data["Time"] = pd.to_datetime(self.predicted_rainfall_data["Time"])

            self.predicted_rainfall_data.set_index(keys=["Time"], inplace=True)
            self.predicted_rainfall_data.resample(self.sample_time).interpolate()
            self.predicted_rainfall_data = self.predicted_rainfall_data[self.predicted_rainfall_data.columns[3:7]]

            self.predicted_rainfall_data["time_hour"] = self.predicted_rainfall_data.index.hour.astype(float)

        max_data_len = min(len(self.predicted_rainfall_data), len(self.actual_rainfall_data), len(self.inflow))
        self.actual_rainfall_data = self.actual_rainfall_data.iloc[:max_data_len - 1]
        self.predicted_rainfall_data = self.predicted_rainfall_data.iloc[:max_data_len - 1]
        self.inflow = self.inflow.iloc[:max_data_len - 1]

        if self.x_shape is None:
            x, y = self.__getitem__(48)
            # Shape is (batch_size, time, features)
            self.x_shape = (None, *np.shape(x))
            self.y_shape = (None, *np.shape(y))

    def get_initiate_data(self, t):
        level_at_t = self.level[t]
        volume_at_t = self.level_to_volume(level_at_t)
        print(f"pump: {self.pump_station_name} has the following stats:\n"
              f"min volume: {self.min_volume}: (level: {self.min_level})\n"
              f"max volume: {self.max_volume}: (level: {self.max_level})\n"
              f"start volume: {volume_at_t}: (level: {level_at_t})\n"
              f"pump speed: {self.pump_speed}\n"
              )
        return self.min_volume, self.max_volume, self.pump_speed, volume_at_t

    def level_to_volume(self, level):

        idx = bisect.bisect_left(self.volume["cm"], level)
        idx = max(0, min(len(self.volume["cm"]) - 1, idx))
        closest_volume = self.volume["m3"][idx]
        return closest_volume

    def validation_iterator(self, start, end):
        return self.iterator(np.linspace(start=start, stop=end, num=end - start, dtype=np.int), batch_size=1)

    def train_iterator(self, batch_size, dry_days, wet_days):
        train_ts, _ = utils.get_test_train_on_inflow(self.inflow,
                                                     dry_days,
                                                     wet_days)
        return self.iterator(train_ts, batch_size=batch_size)

    def test_iterator(self, batch_size, dry_days, wet_days):
        _, test_ts = utils.get_test_train_on_inflow(self.inflow,
                                                    dry_days,
                                                    wet_days)
        return self.iterator(test_ts, batch_size=batch_size)

    def iterator(self, dates, batch_size):
        """
        Iterates of the given dates (as index) and returns the data from those dates
        :param dates: The time steps this iterator goes trough
        :param batch_size: The amount of time steps per call are returned
        :return: data from __getitem__
        """
        dates = dates.copy()
        print(len(dates))
        if len(dates):
            while len(dates) != 0:
                x_train = []
                y_true = []
                for i in range(min(batch_size, len(dates))):
                    date = int(dates.pop())
                    x, y = self.__getitem__(date)
                    x_train.append(x)
                    y_true.append(y)

                x_train, y_true = np.array(x_train), np.array(y_true)

                yield x_train, y_true
        else:
            x_train, y_true = self.__getitem__(100)
            yield np.expand_dims(x_train, axis=0), np.expand_dims(y_true, axis=0)

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
