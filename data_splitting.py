import numpy as np
import pandas as pd
from datetime import datetime

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

# def split_train_test(df):
#     '''Takes a dataframe with split date columns and splits it in the
#     following way: for every month, take the last 7 consecutive days.'''

month_groups = new_rainfall_data.groupby(['Year', 'Month'])
final_days = month_groups.tail(n=7)
print(final_days[['Time', 'Year', 'Month', 'Day']])
