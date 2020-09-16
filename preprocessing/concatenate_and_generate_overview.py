import pandas as pd
import re
import os
from dateutil.parser import parse

dirs = [
    '..',
    'data'
]


def search_and_concat(location):
    """
    Searches for table files and parses them into dataframes
    Also generating a overview file

    :param location: array or str, containing strings that are joined together to form the path or just a string
    """
    dataframes = {}
    if isinstance(location, list):
        location = os.path.join(*location)
    list_dir = os.listdir(location)
    print(f'Searching for tables in {location}...')

    for item in list_dir:
        file_path = os.path.join(location, item)
        if os.path.isdir(file_path):
            search_and_concat(file_path)
        else:
            dataframes = read_file(dataframes, file_path, location)

    save_and_make_overview(dataframes)


def read_file(dataframes, file_path, location):
    """
    Read a csv or excel file and write the new dataframe to the preprocessing folder

    :param dataframes: array of DataFrames
    :param file_path: str, path to the file
    :param location: str, the folder in which the file is in
    """

    filename, file_extension = os.path.splitext(file_path)
    if file_extension == '.xlsx' or file_extension == '.csv':

        # Find out if file satisfies the regex for given datasets
        result = find_rainfall_download(file_path, file_extension)
        if result is None:
            is_download = False
            result = find_standard_group(file_path, file_extension)

            if result is None:
                result = find_temp_group(file_path, file_extension)

                if result is None:
                    print(f"No regex found for file {file_path}")
        else:
            is_download = True

        if result is not None:
            file_group = result.group(1)
        else:
            file_group = filename

        new_file = file_group.replace(f"..{os.path.sep}", "").replace(f"{os.path.sep}", "_")
        if is_already_parsed(new_file):
            print(f"Already parsed {new_file}.csv")
            return dataframes

        # Read as excel if file is excel, otherwise read as csv
        if file_extension == '.xlsx':
            table = pd.read_excel(file_path)
        else:
            table = read_csv(file_path, is_download)

        if table.columns[0] == 'Column1':
            table.columns = table.iloc[9]
            table = table[10:].reset_index(drop=True)
        elif table.columns[0] == 'Waterschap Aa en Maas':
            table.columns = table.iloc[8].fillna('')
            table = table[9:].reset_index(drop=True)

        dataframes = save_table(table, result, location, new_file, dataframes)

    return dataframes


def save_table(table, result, location, new_file, dataframes):
    """
    Saves the table to a file in the preprocessing folder

    :param table: pandas DataFrame, the table to be saved
    :param result: regex result, of a possible found group
    :param location: str, location of the original file
    :param new_file: str, name of saved file
    :param dataframes: array of pandas DataFrames, the possibly get the rest of the group data
    """
    table = set_unique_column_to_index(table)
    if table is None:
        log_error(f"ERROR: table is empty {new_file}")
        return dataframes
    if result is not None:
        print(f"Found group: {result.group(1)}")
        if result.group(1) not in dataframes:
            dataframes[result.group(1)] = pd.DataFrame()
        old_df = dataframes[result.group(1)]
        dataframes[result.group(1)] = pd.concat([old_df, table]).drop_duplicates()
        if len(dataframes[result.group(1)]) != len(old_df) + len(table):
            log_error(f"ERROR: found duplicate rows in concatenating {new_file}")
    else:
        overview_location = os.path.join('processed', '1. Overview.xlsx')
        overview = pd.read_excel(overview_location, index_col=0)
        overview = overview.append({
            'location': location,
            'columns': ', '.join(table.columns),
            'nr_rows': len(table)
        }, ignore_index=True).drop_duplicates()
        overview.to_excel(overview_location)
        table.to_csv(os.path.join('processed', f"{new_file}.csv"))

    return dataframes


def read_csv(file_path, is_download):
    """
    Reads a csv file and decides the correct delimiters

    :param file_path: str, the path to the original file
    :param is_download: bool, whether the file is in the rainfall download group
    """
    with open(file_path, 'r') as file:
        data = file.read().replace('\n', '')
        p = re.compile("^[^,]*;")
        result_del = p.search(data)

        if result_del is not None:
            if data[0:8] == 'Locatie;':
                table = pd.read_csv(file_path, delimiter=";", decimal=",", header=7)
                table = table[:-2]
            else:
                table = pd.read_csv(file_path, delimiter=";", decimal=",")
        else:
            if is_download:
                table = pd.read_csv(file_path, skiprows=2)
            else:
                table = pd.read_csv(file_path)
        return table


def is_already_parsed(filename):
    """
    Check if the file already exist in the preprocessing folder

    :param filename: str, the filename of the original file
    """
    new_file = filename.replace(f"..{os.path.sep}", "").replace(f"{os.path.sep}", "_")
    new_dir = os.path.join('processed', f"{new_file}.csv")
    if os.path.exists(new_dir):
        return True
    return False


def find_rainfall_download(file_path, file_extension):
    """
    Check if file is a rainfall download file

    :param file_path: str, the filepath
    :param file_extension: str, the extension of the file
    """
    regex = f"(.*Download__).*\{file_extension}"
    p = re.compile(regex)
    return p.search(file_path)


def find_standard_group(file_path, file_extension):
    """
    Check if file belongs to a standard grouped file

    :param file_path: str, the filepath
    :param file_extension: str, the extension of the file
    """
    regex = f"(.*_[a-zA-Z]*)[0-9]*\{file_extension}"
    p = re.compile(regex)
    return p.search(file_path)


def find_temp_group(file_path, file_extension):
    """
    Check if filename belongs to 'temp' files

    :param file_path: str, the filepath
    :param file_extension: str, the extension of the file
    """
    regex = f"(.*Temp)[0-9]*\{file_extension}"
    p = re.compile(regex)
    return p.search(file_path)


def save_and_make_overview(dfs):
    """
    Saves the dataframes to csv files and make an overview in Overview.xlsx

    :param dfs: array of panda DataFrames
    """
    overview_location = os.path.join('processed', '1. Overview.xlsx')
    overview = pd.read_excel(overview_location, index_col=0)
    for df_location in dfs:
        new_location = df_location.replace(f"..{os.path.sep}", "").replace(f"{os.path.sep}", "_")
        if dfs[df_location].empty:
            log_error(f"{df_location} is empty...")
            continue
        overview = overview.append({
            'location': df_location,
            'columns': ', '.join(dfs[df_location].columns),
            'nr_rows': len(dfs[df_location])
        }, ignore_index=True).drop_duplicates()
        if 'Unnamed: 0' in dfs[df_location].columns or dfs[df_location].index.name == 'Unnamed: 0':
            dfs[df_location].to_csv(os.path.join("processed", f"{new_location}.csv"), index=False)
        else:
            dfs[df_location].sort_index().to_csv(os.path.join("processed", f"{new_location}.csv"))

    overview.to_excel(overview_location)


def set_unique_column_to_index(df):
    """
    Finds a column that only has unique values and makes this the index of the dataframe

    :param df: pandas DataFrame
    """
    if len(df.columns) == 0:
        print("ERROR only 0 columns")
        return

    if len(df) == 0:
        print("Error only 0 rows")
        return

    if 'Time' in df.columns:
        index_column = 'Time'
    elif 'Unnamed: 0' in df.columns:
        index_column = 'Unnamed: 0'
    elif 'DAG' in df.columns:
        index_column = 'DAG'
    elif 'dem' in df.columns:
        index_column = 'dem'
    elif 'TimeStamp' in df.columns:
        index_column = 'TimeStamp'
    elif 'datumBeginMeting' in df.columns:
        index_column = 'datumBeginMeting'
    else:
        index_column = df.nunique().sort_values(ascending=False).index[0]

    if (not isinstance(df.loc[0, index_column], int)
            and not isinstance(df.loc[0, index_column], float)
            and is_date(str(df.loc[0, index_column]))):
        df[index_column] = pd.to_datetime(df[index_column])
    df.set_index(index_column, inplace=True)

    return df


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

    :param string: str, string to log
    """
    f = open("error.log", "a")
    f.write(f"{string} \n")
    f.close()


search_and_concat(dirs)
