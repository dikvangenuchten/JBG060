class DataHandler:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.x_shape = (5, 48)

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