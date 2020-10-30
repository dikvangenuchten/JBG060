from preprocessing.data_splitting import *
from preprocessing.RainfallPreprocessing import *
from preprocessing.Rainbuckets import *
from preprocessing.unzipify import *
from preprocessing.concatenate_and_generate_overview import *

if __name__ == '__main__':
    data_path = "data"

    # Unzip in data folder
    search_and_unzip(data_path)

    # Concatenate files and move to processed
    search_and_concat(data_path)

    # Convert rainfall data to hourly
    predictions_dataFrame = predictions()
    predictions_dataFrame.to_csv('processed\\rainfallpredictionsHourly.csv')

    # Split data into 80-20 split
    rainfall_data = pd.read_csv('processed\\rainfallpredictionsHourly.csv')
    train_data, test_data = split_weeks(rainfall_data, 8, 2)
    train_data.to_csv("processed\\train_data.csv")
    test_data.to_csv("processed\\test_data.csv")
