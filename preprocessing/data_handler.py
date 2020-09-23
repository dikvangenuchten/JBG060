import os
import pandas as pd

class DataHandler:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.x_shape = (5, 48)
        self.flow_df = None
        self._get_flow(10)

    def load_data(self):
        """"
        Loads the data into memory
        """
        pass

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

    def _get_flow(self, t, delta=48,
                  csv_location=os.path.join('preprocessing', 'processed', 'helftheuvel_1hour.csv'),
                  flow_column='helftheuvelweg'):
        """
        Returns the flow between t and t+48 were t=0 is the beginning of the dataset, being 2018-01-01 00:00
        :param t: int, is the index from which point we want to get the data from
        :param delta: int, the amount of rows after t we want to get the data from
        :param csv_location: str, the amount of rows after t we want to get the data from
        """
        if self.flow_df is None:
            self.flow_df = pd.read_csv(csv_location, index_col=0)[flow_column]
        print(self.flow_df[t:t+delta])
        return self.flow_df[t:t+delta]
