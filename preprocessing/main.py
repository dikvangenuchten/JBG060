from preprocessing.data_splitting import *
from preprocessing.RainfallPreprocessing import *
from preprocessing.Rainbuckets import *
from preprocessing.unzipify import *
from preprocessing.concatenate_and_generate_overview import *
from preprocessing.calculate_level_cm_to_m3 import *
from preprocessing.calculate_pump_in_flow import *


def preprocessing_main():
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

    # Calculation of approximated in flow for every pump
    if not os.path.exists('processed\\full_level.csv'):
        create_full_level('processed\\')
    full_level = pd.read_csv('processed\\full_level.csv')
    pumps = ['Helftheuvel', 'Engelerschans', 'Maaspoort', 'Rompert', 'Oude Engelenseweg']
    for pump in pumps:
        pump_flow = get_in_flow_approximation(pump, full_level, 'processed\\')
        pump_flow.to_csv(f"processed\\pump_in_flow_appr_{pump}.csv")

    # Calculates the conversion dataframe from level cm to m3 for every pump
    pumps = ['Engelerschans', 'Maaspoort', 'Rompert', 'Oude Engelenseweg', 'Helftheuvel']
    for pump in pumps:
        pump_df = calculate_single_cm_to_m3(pump)
        pump_df.to_csv(f"processed\\{pump}_single_cm_m3.csv")


if __name__ == '__main__':
    preprocessing_main()
