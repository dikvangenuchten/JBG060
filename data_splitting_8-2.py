import pandas as pd

rainfall_data = pd.read_csv('rainfallpredictions1_1.csv')

def create_weeks(df, column: str):
    '''Takes a dataframe and a column that contains a time string, then extracts
    the week number based on this column and adds this to the existing dataframe.'''

    #Drop the first row of the dataframe for logistic purposes
    df = df.drop([0])
    df['Week_nr'] = pd.DatetimeIndex(df[column]).week

    return df

new_rainfall_data = create_weeks(rainfall_data, 'Time')
print(new_rainfall_data[['Time', 'Week_nr']])