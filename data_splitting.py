import pandas as pd

rainfall_data = pd.read_csv('rainfallpredictions1_1.csv')

def split_date_column(df, column: str):
    '''Takes a dataframe and the column in which a date can be found,
    converts this date into a datetime object, and then splits the object
    into year, month, and date columns.'''

    #Format each row in the 'Time' column into a datetime object
    df['Year'] = pd.DatetimeIndex(df[column]).year
    df['Month'] = pd.DatetimeIndex(df[column]).month
    df['Day'] = pd.DatetimeIndex(df[column]).day

    return df

new_rainfall_data = split_date_column(rainfall_data, 'Time')

def create_test_data(df, final_days: int):
    '''Takes a dataframe with split date columns and creates test data in the
    following way: for every month, take the last 7 consecutive days.'''

    month_groups = df.groupby(['Year', 'Month'])
    test_data = month_groups.tail(n = final_days)

    return test_data

test_data = create_test_data(new_rainfall_data, 7)

def create_train_data(df, test_df):
    '''Creates the training data by removing the rows that are already
    in the test dataframe made by the create_test_data function.'''

    indexed_test_data = test_df.reset_index()
    index_list = indexed_test_data['index'].tolist()
    train_data = df.drop(index_list)

    return train_data

train_data = create_train_data(new_rainfall_data, test_data)




