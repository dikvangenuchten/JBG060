import pandas as pd
import re
import os
import csv

# TODO make one overview file

data_location = '../data/'
dataframes = {}


def search_and_concat(location):
    """
    Searches for table files and parses them into dataframes
    Also generating a overview file
    """
    list_dir = os.listdir(location)
    print(f'Searching for tables in {location}...')

    for item in list_dir:
        if os.path.isdir(location + item):
            search_and_concat(f'{location}{item}/')
        else:
            filename, file_extension = os.path.splitext(f"{location}{item}")
            if file_extension == '.xlsx' or file_extension == '.csv':

                # Find out if file satisfies the regex for given datasets
                regex = f"(.*Download__).*\{file_extension}"
                p = re.compile(regex)
                result = p.search(f"{location}{item}")

                if (result is not None):
                    log_error(f"ERROR: {location}{item}, cannot be parsed into dataframe (1)")
                    continue

                if result is None:
                    regex = f"(.*_[a-zA-Z]*)[0-9]*\{file_extension}"
                    p = re.compile(regex)
                    result = p.search(f"{location}{item}")

                    if result is None:
                        # Find Tempxxxxxxx.csv files
                        regex = f"(.*Temp)[0-9]*\{file_extension}"
                        p = re.compile(regex)
                        result = p.search(f"{location}{item}")
                        if result == None:
                            log_error(f"No regex found for file {location}{item}")
                            print(f"No regex found for file {location}{item}")

                if result is not None:
                    # Check if file already exists, if so the data is already parsed previously
                    new_file = result.group(1).replace("../", "").replace("/", "_")
                    if (os.path.exists(f"processed/{new_file}.csv")):
                        print(f"Already parsed {result.group(1)}")
                        continue
                else:
                    new_file = filename.replace("../", "").replace("/", "_")
                    if os.path.exists(f"processed/{new_file}.csv"):
                        print(f"Already parsed {new_file}.csv")
                        continue

                # Read as excel if file is excel, otherwise read as table
                if file_extension == '.xlsx':
                    table = pd.read_excel(f"{location}{item}")
                else:
                    with open(f"{location}{item}", 'r') as file:
                        data = file.read().replace('\n', '')
                        p = re.compile("^[^,]*;")
                        result_del = p.search(data)

                        if result_del is not None:
                            table = pd.read_csv(f"{location}{item}", delimiter=";", decimal=",")
                        else:
                            table = pd.read_csv(f"{location}{item}")

                if table.columns[0] == 'Column1':
                    table.columns = table.iloc[9]
                    table = table[10:].reset_index(drop=True)

                table = set_unique_column_to_index(table)
                if table is None:
                    log_error(f"ERROR: table is empty {location}{item}")
                    continue
                if result is not None:
                    print(f"Found group: {result.group(1)} Item: {item}")
                    if result.group(1) not in dataframes:
                        dataframes[result.group(1)] = pd.DataFrame()
                    old_df = dataframes[result.group(1)]
                    dataframes[result.group(1)] = pd.concat([old_df, table])
                    if len(dataframes[result.group(1)]) != len(old_df) + len(table):
                        log_error(f"ERROR: found duplicate rows in concatenating {location}{item}")
                else:
                    table.to_csv(f"processed/{new_file}.csv")

    save_and_make_overview(dataframes)


def save_and_make_overview(dfs):
    overview = pd.read_excel("processed/1. Overview.xlsx", index_col=0)
    for df_location in dfs:
        new_location = df_location.replace("../", "").replace("/", "_")
        if (dfs[df_location].empty):
            log_error(f"{df_location} is empty...")
            continue
        overview = overview.append({
            'location': df_location,
            'columns': ', '.join(dfs[df_location].columns),
            'nr_rows': len(dfs[df_location])
        }, ignore_index=True)
        dfs[df_location].to_csv(f"processed/{new_location}.csv")
    overview.to_excel("processed/1. Overview.xlsx")


def set_unique_column_to_index(df):
    """
    Finds a column that only has unique values and makes this the index of the dataframe
    """
    if len(df.columns) == 0:
        print("ERROR only 0 columns")
        return

    if len(df) == 0:
        print("Error only 0 rows")
        return

    index_column = df.nunique().sort_values(ascending=False).index[0]

    if (not isinstance(df.loc[0, index_column], int)
            and not isinstance(df.loc[0, index_column], float)
            and is_date(df.loc[0, index_column])):
        df[index_column] = pd.to_datetime(df[index_column])
    df.set_index(index_column, inplace=True)

    return df


from dateutil.parser import parse


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def log_error(string):
    """
    Writes the error message to the error log file
    """
    f = open("error.log", "a")
    f.write(f"{string} \n")
    f.close()


search_and_concat(data_location)
