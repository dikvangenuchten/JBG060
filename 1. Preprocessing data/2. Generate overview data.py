import pandas
import re
import os

data_location = '../data/'
dataframes = {}

def search_and_analyse(location):
    list_dir = os.listdir(location)
    print(f'Searching for tables in {location}...')

    for item in list_dir:
        if os.path.isdir(location + item):
            search_and_analyse(f'{location}{item}/')
        else:
            filename, file_extension = os.path.splitext(location + item)
            if file_extension == '.xlsx' or file_extension == '.csv':
                regex = f"(.*Download__).*\{file_extension}"
                p = re.compile(regex)
                result = p.search(location + item)

                if result == None:
                    regex = f"(.*_[a-zA-Z]*)[0-9]*\{file_extension}"
                    p = re.compile(regex)
                    result = p.search(location + item)

                    if result == None:
                        # Find Tempxxxxxxx.csv files
                        regex = f"(.*Temp)[0-9]*\{file_extension}"
                        p = re.compile(regex)
                        result = p.search(location + item)
                        if result == None:
                            print(f"No regex found for file {location + item}")

                # Read as excel if file is excel, otherwise read as table
                if file_extension == '.xlsx':
                    table = pandas.read_excel(location + item)
                else:
                    table = pandas.read_table(location + item)

                if (result != None):
                    print(f"Found! {result.group(1)}")
                    if (result.group(1) not in dataframes):
                        dataframes[result.group(1)] = pandas.DataFrame()
                    dataframes[result.group(1)] = pandas.concat([dataframes[result.group(1)],table]).drop_duplicates()

# TODO save unique column and check whether there are duplicates, if so report back
# TODO save tables to files
# TODO make one overview file

search_and_analyse(data_location)
print(dataframes)