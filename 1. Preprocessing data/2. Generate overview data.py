import pandas
import re
import os

data_location = '../data/'


def search_and_analyse(location):
    list_dir = os.listdir(location)
    print(f'Searching for tables in {location}...')

    for item in list_dir:
        if os.path.isdir(location + item):
            search_and_analyse(f'{location}{item}/')
        else:
            filename, file_extension = os.path.splitext(location + item)
            if file_extension == '.xlsx' or file_extension == '.csv':
                regex = f"(.*_[a-zA-Z]*)[0-9]*\{file_extension}"
                p = re.compile(regex)
                result = p.search(location + item)

                if result != None:
                    print(result.group(1))
                else:
                    print(f"No regex found for file {location + item}")

                if file_extension == '.xlsx':
                    table = pandas.read_excel(location + item)
                else:
                    table = pandas.read_table(location + item)


search_and_analyse(data_location)
