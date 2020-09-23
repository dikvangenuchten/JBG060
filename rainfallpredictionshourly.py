import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#predictions:
    
#opening the data for harmonie predictions 
Harmonie= []
Harmonie.append(pd.read_csv('rainfall/rainfall/2018_harmonie_juli_augustus_predictions.csv',';'))
Harmonie.append(pd.read_csv('rainfall/rainfall/2019_harmonie_juli_augustus_predictions.csv',','))
Harmonie.append(pd.read_csv('rainfall/rainfall/2020_harmonie_juli_augustus_predictions.csv',','))
Harmonie = pd.concat(Harmonie)

#removing errors
Harmonie = Harmonie.replace(float(-9999.0),np.nan)
#implementing averages
predsonly = Harmonie.drop(['ModelDate','Time'],axis=1)
Harmonie['avg'] = predsonly.sum(axis=1)/len(predsonly.columns)

#Setting inline
Harmonie = Harmonie[['ModelDate','Time','avg']]

#opening the data for hirlam predictions
Hirlam = []
Hirlam.append(pd.read_csv('rainfall/rainfall/2018_hirlam_predictions.csv',';'))
Hirlam.append(pd.read_csv('rainfall/rainfall/2019_hirlam_predictions.csv',','))
Hirlam.append(pd.read_csv('rainfall/rainfall/2020_hirlam_predictions.csv',','))
Hirlam = pd.concat(Hirlam)

#removing errors
Hirlam = Hirlam[Hirlam['Prediction']>-2]

def getRainfallPredictionshr(data: pd.DataFrame)->list:
    #str to datetime conversions
    data['ModelDate'] = pd.to_datetime(data['ModelDate'],format='%Y-%m-%d %H',exact=True)
    data['Time'] = pd.to_datetime(data['Time'],format='%Y-%m-%d %H',exact=True)
    #calculate x hour in advance prediction
    data['tdiff'] = data['ModelDate'] - data['Time'].dt.normalize()
    
    #sort by individual predictions
    data_datediff = data.groupby(data['tdiff'])
    
    
    frames = []
    #do in dayly insead of hourly
    for diff in data_datediff:
        diff = diff[1].reset_index().drop('index',axis=1)
        print(type(diff['Time'][0]))
        frames.append(pd.DataFrame(diff))
    return frames
"""
Turns the raw dataframes into the proper form, hourly.
"""

#get predictions
pred_harmonie = getRainfallPredictionshr(Harmonie)
pred_hirlam = getRainfallPredictionshr(Hirlam)




#actual data

#loading data
actualfiles = os.listdir(os.getcwd()+'\\rainfall'+'\\rainfall'+'\\rain_timeseries')
actual = []
for file in actualfiles:
    actual.append(pd.read_csv('rainfall/rainfall/rain_timeseries/'+file,skiprows =2))
actual = pd.concat(actual)

#process the actual rainfall into hourly format.
actual['Begin'] = pd.to_datetime(actual['Begin'],dayfirst=True)
actual_hrs = actual.resample('H',on='Begin').sum()
actual_hrs['total'] =actual_hrs.loc[:,list(actual_hrs.columns)[1:433]].sum(axis=1)
actual_hrs['avg'] =actual_hrs['total']/len(list(actual_hrs.columns)[1:433])
actual_hrs.reset_index()


#get predictions
preds = pd.DataFrame()
preds[['Time','actual']] = actual_hrs.reset_index()[['Begin','avg']]
preds['Time'] = pd.to_datetime(preds['Time'],format='%Y-%m-%d %H',exact=True)


for frame in pred_hirlam:
    frame[f'hirlam_pred {frame["tdiff"][0]}'] = frame['Prediction']
    preds = preds.merge(frame[['Time',f'hirlam_pred {frame["tdiff"][0]}']],on='Time',how='left')
for frame in pred_harmonie:
    frame[f'harmonie_pred {frame["tdiff"][0]}'] = frame['avg']
    preds = preds.merge(frame[['Time',f'harmonie_pred {frame["tdiff"][0]}']],on='Time',how='left')
preds
