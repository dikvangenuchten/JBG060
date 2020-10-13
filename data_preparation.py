import pandas as pd
import os

#create full level csv
path = 'processed/'
files = os.listdir(path)
frames = []
for file in files:
    if 'level' in file:
        file = pd.read_csv(f'{path}/{file}')
        frames.append(file)

full_level = pd.concat(frames, ignore_index=True)
full_level['Datum'] = pd.to_datetime(full_level['Datum'])
full_level['Tijd'] = pd.to_datetime(full_level['Tijd'])
full_level['Tijd'] = full_level['Tijd'].dt.time
full_level.sort_values(by=['Datum', 'Tijd'], inplace = True)
full_level['Datum'] = full_level['Datum'].astype(str)
full_level['Tijd'] = full_level['Tijd'].astype(str)
full_level.reset_index(drop=True,inplace=True)


# Function to select all level data from one pump
def get_pump_level(pump: str, sample_time='1h')->pd.DataFrame:
    """Creates a dataframe with all level data for one pump"""

    pump_level = full_level.loc[:, full_level.columns.str.contains(f'{str(pump)}|Tijd|Datum')]

    pump_level['date+time'] = pump_level['Datum'] + ' ' + pump_level['Tijd']

    pump_level['date+time'] = pd.to_datetime(pump_level['date+time'])

    pump_level.set_index('date+time', drop=True, inplace=True)
    pump_level = pd.DataFrame(pump_level.resample(sample_time).mean())
    pump_level['level_diff'] = pump_level.diff()
    print('pump level done')
    return pump_level


# function to get all flow data from one pump
def get_flow_data(pump: str, sample_time='1h')->pd.DataFrame:
    """Creates data frame with all flow data for one pump"""
    files = os.listdir(path)
    frames = []
    for file in files:
        if 'flow' and pump in file:
            file = pd.read_csv(f'{path}/{file}')
            frames.append(file)

    flow_data = pd.concat(frames, ignore_index=True)
    flow_data['datumBeginMeting'].fillna(flow_data['dem'], inplace=True)
    flow_data['datumBeginMeting'] = pd.to_datetime(flow_data['datumBeginMeting'])
    flow_data.sort_values(by=['datumBeginMeting'], inplace=True)
    flow_data = flow_data[['datumBeginMeting', 'hstWaarde']].set_index('datumBeginMeting')
    flow_data = flow_data.resample(sample_time).mean()
    print('flow data done')
    return flow_data



def pump_flow_level(pump: str, sample_time='1h')-> Union[str, DataFrame]:
    """"Combines both level and flow dataframes to one dataframe"""
    
    dct = {'Helftheuvel': ['003', '301'], 'Engelerschans': ['004', 'FIT201'], 'Maaspoort': ['006', '501'],
           'Rompert': ['005', '501'], 'Oude Engelenseweg': ['002', '401']}

    if pump not in dct.keys():
        return f'Pump name not recognized, try one of these {dct.keys()}'

    df_level = get_pump_level(dct[pump][0])
    df_flow = get_flow_data(dct[pump][1])

    df_flow_level = pd.merge(df_level, df_flow, how='inner', left_index=True, right_index=True)
    return df_flow_level



