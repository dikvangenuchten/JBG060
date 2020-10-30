import pandas as pd


def split_date_column(df, column: str):
    '''Takes a dataframe and the column in which a date can be found,
    converts this date into a datetime object, and then splits the object
    into year, month, and date columns.'''

    # Format each row in the 'Time' column into a datetime object
    df['Year'] = pd.DatetimeIndex(df[column]).year
    df['Month'] = pd.DatetimeIndex(df[column]).month
    df['Day'] = pd.DatetimeIndex(df[column]).day

    return df


def create_test_data(df, final_days: int):
    '''Takes a dataframe with split date columns and creates test data in the
    following way: for every month, take the last 7 consecutive days.'''

    # Drop the 2017 entry (should be in training)
    df = df.drop(df[df['Year'] == 2017].index)

    # Filter out the final month, because this month is not complete
    final_month = df[(df['Year'] == 2020) & (df['Month'] == 8)]
    final_month_n = ((final_days - 5)) * 24 + 22  # 5 missing days, 1 with 22 hours
    test_final_month = final_month.tail(final_month_n)

    # Drop the final month and create groups, then take the n last days
    df_no_final = df.drop(final_month.index)
    month_groups = df_no_final.groupby(['Year', 'Month'])
    test_other = month_groups.tail(final_days * 24)

    # Concat final month with the other months
    test_data = pd.concat([test_other, test_final_month])

    return test_data


def create_train_data(df, test_df):
    '''Creates the training data by removing the rows that are already
    in the test dataframe made by the create_test_data function.'''

    indexed_test_data = test_df.reset_index()
    index_list = indexed_test_data['index'].tolist()
    train_data = df.drop(index_list)

    return train_data


if __name__ == '__main__':
    rainfall_data = pd.read_csv('rainfallpredictionsHourlyV3.csv')
    new_rainfall_data = split_date_column(rainfall_data, 'Time')
    test_data = create_test_data(new_rainfall_data, 7)
    train_data = create_train_data(new_rainfall_data, test_data)
