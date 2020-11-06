# required libraries
import pandas as pd
import os
import numpy as np


def loadHarmonie(path_to_rainfall: str = 'data/rainfall/') -> pd.DataFrame:
    """opening and concatenating the data for harmonie predictions (only predicts juli-august)
    path_to_rainfall is a path to the folder with all rainfall predictions, standard: data/rainfall/"""
    Harmonie = []
    Harmonie.append(pd.read_csv(path_to_rainfall + '2018_harmonie_juli_augustus_predictions.csv', ';'))
    Harmonie.append(pd.read_csv(path_to_rainfall + '2019_harmonie_juli_augustus_predictions.csv', ','))
    Harmonie.append(pd.read_csv(path_to_rainfall + '2020_harmonie_juli_augustus_predictions.csv', ','))
    Harmonie = pd.concat(Harmonie)

    # removing errors
    Harmonie = Harmonie.replace(float(-9999.0), np.nan)
    # implementing averages
    predsonly = Harmonie.drop(['ModelDate', 'Time'], axis=1)
    Harmonie['avg'] = predsonly.sum(axis=1) / len(predsonly.columns)

    # Setting inline
    Harmonie = Harmonie[['ModelDate', 'Time', 'avg']]
    return Harmonie


def loadHirlam(path_to_rainfall: str = 'data/rainfall/') -> pd.DataFrame:
    """opening and concatenating the data for hirlam predictions
    path_to_rainfall is a path to the folder with all rainfall predictions, standard: data/rainfall/"""
    Hirlam = []
    Hirlam.append(pd.read_csv(path_to_rainfall + '2018_hirlam_predictions.csv', ';'))
    Hirlam.append(pd.read_csv(path_to_rainfall + '2019_hirlam_predictions.csv', ','))
    Hirlam.append(pd.read_csv(path_to_rainfall + '2020_hirlam_predictions.csv', ','))
    Hirlam = pd.concat(Hirlam)

    # removing errors
    Hirlam = Hirlam.replace(float(-9999.0), np.nan)
    return Hirlam


#############################

# processes prediction data from hourly to daily
def get_rainfall_predictions(data: pd.DataFrame) -> list:
    """Processes the prediction data into a suitable format for processing, requires the data from either
    LoadHirlam or LoadHarmonie as input"""
    # str to datetime conversions
    data['ModelDate'] = pd.to_datetime(data['ModelDate'], format='%Y-%m-%d %H', exact=True)
    data['Time'] = pd.to_datetime(data['Time'], format='%Y-%m-%d %H', exact=True)
    # calculate x hour in advance prediction
    data['tdiff'] = data['ModelDate'] - data['Time'].dt.normalize()

    # sort by individual predictions
    data_datediff = data.groupby(data['tdiff'])

    frames = []
    # do in dayly insead of hourly
    # separates by difference in time between model creation and prediction time
    for diff in data_datediff:
        data_day = []
        # generates a new row for the entire day from all the hourly predictions
        for group in diff[1].groupby(diff[1]['Time'].dt.normalize()):
            newline = group[1].sum(axis=0)
            newline['tdiff'] = abs(newline['tdiff'] / len(group[1]) - pd.Timedelta(hours=18))
            newline['Time'] = group[0]
            data_day.append(newline)
        frames.append(pd.DataFrame(data_day))
    # list of dataframes with one frame per model prediction (e.g. made 1d12h or 2d before)
    return frames


def loadActualRainfall(path_to_rain_timeseries: str = 'data/rainfall/rain_timeseries/') -> pd.DataFrame:
    """Loads the files containing the actual factual rainfall data, takes as input a path to where this data is kept,
     should normally be in the rain_timeseries folder"""
    actualfiles = os.listdir(os.getcwd() + '/' + path_to_rain_timeseries)
    actual = []
    for file in actualfiles:
        actual.append(pd.read_csv(path_to_rain_timeseries + '/' + file, skiprows=2))
    actual = pd.concat(actual)
    return actual


def cleanActualRainfall(actual_rainfall: pd.DataFrame) -> pd.DataFrame:
    """Makes the actual rainfall data ready for processing, takes as input data from the loadActualRainfall function"""
    actual_rainfall['Begin'] = pd.to_datetime(actual_rainfall['Begin'], dayfirst=True)
    # sorting and cleaning
    actual_rainfall = actual_rainfall.sort_values(by='Begin')
    actual_rainfall = actual_rainfall.reset_index()
    actual_rainfall = actual_rainfall.drop(['index'], axis=1)

    # converting to days (takes an assload of time)
    actual_days = []
    for group in actual_rainfall.groupby(actual_rainfall['Begin'].dt.normalize()):
        newline = group[1].sum(axis=0)
        newline['Begin'] = group[0]
        newline['Eind'] = newline['Eind'][-19:]
        actual_days.append(newline)
    actual_days = pd.DataFrame(actual_days)

    # getting the avg daily rain
    actual_days['total'] = actual_days.loc[:, list(actual_days.columns)[3:436]].sum(axis=1)
    actual_days['avg'] = actual_days['total'] / len(list(actual_days.columns)[3:436])
    return actual_days


def predictions(location_Hirlam: str = 'data/rainfall/', location_Harmonie: str = 'data/rainfall/',
                location_rain_time_series_data: str = 'data/rainfall/rain_timeseries') -> pd.DataFrame:
    """loads both predictions and actual data and compiles them into one file suitable for further processing,
    requires the place where:
    the hirlam is stored as: location_Hirlam
    the harmonie is stored as: locaton_Harmonie
    the actual rainfall data is stored as: location_rain_timeseriesdata"""
    pred_harmonie = get_rainfall_predictions(loadHarmonie(location_Harmonie))
    pred_hirlam = get_rainfall_predictions(loadHirlam(location_Hirlam))
    actual = cleanActualRainfall(loadActualRainfall(location_rain_time_series_data))

    preds = pd.DataFrame()
    preds[['Time', 'actual']] = actual[['Begin', 'avg']]

    # merging the frames
    for frame in pred_hirlam:
        frame[f'hirlam_pred {frame["tdiff"][0]}'] = frame['Prediction']
        preds = preds.merge(frame[['Time', f'hirlam_pred {frame["tdiff"][0]}']], on='Time', how='left')
    for frame in pred_harmonie:
        frame[f'harmonie_pred {frame["tdiff"][0]}'] = frame['avg']
        preds = preds.merge(frame[['Time', f'harmonie_pred {frame["tdiff"][0]}']], on='Time', how='left')
    return preds
