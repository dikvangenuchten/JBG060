import pandas

import os

data_location = '../data/'


def search_and_analyse(location):
    list_dir = os.listdir(location)
    print('Searching for tables in {0}...'.format(location))

    for item in list_dir:
        if os.path.isdir(location + item):
            search_and_analyse('{0}{1}/'.format(location, item))
        else:
            if item[-4:] == 'xlsx' or item[-3:] == 'csv':
                print(location + item)
                table = pandas.read_table(location + item)


search_and_analyse(data_location)
