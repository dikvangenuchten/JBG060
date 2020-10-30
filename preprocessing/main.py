from preprocessing.data_splitting import *
from preprocessing.RainfallPreprocessing import *
from preprocessing.Rainbuckets import *
from preprocessing.unzipify import *
from preprocessing.concatenate_and_generate_overview import *

if __name__ == '__main__':
    data_path = "data"

    search_and_unzip(data_path)

    search_and_concat(data_path)

    rainfall_data = pd.read_csv('rainfallpredictions1_1.csv')
    train_data, test_data = split_weeks(rainfall_data, 8, 2)

    predictions_dataFrame = predictions()
    predictions_dataFrame.to_csv('rainfallpredictionsHourlyV3.csv')
