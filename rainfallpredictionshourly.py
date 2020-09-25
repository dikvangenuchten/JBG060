import pandas as pd
import os
import numpy as np


def loadHarmonieData(path:str)->pd.DataFrame:
    """Loads the Harmonie data and cleans it for further processing"""

    #opening the data for harmonie predictions 
    Harmonie= []
    Harmonie.append(pd.read_csv(path+'2018_harmonie_juli_augustus_predictions.csv',';'))
    Harmonie.append(pd.read_csv(path+'2019_harmonie_juli_augustus_predictions.csv',','))
    Harmonie.append(pd.read_csv(path+'2020_harmonie_juli_augustus_predictions.csv',','))
    Harmonie = pd.concat(Harmonie)
    
    #removing errors
    Harmonie = Harmonie.replace(float(-9999.0),np.nan)
    #implementing averages
    predsonly = Harmonie.drop(['ModelDate','Time'],axis=1)
    Harmonie['Prediction'] = predsonly.sum(axis=1)/len(predsonly.columns)
    
    #Setting inline
    Harmonie = Harmonie[['ModelDate','Time','Prediction']]
    return Harmonie



def loadHirlamData(path:str)->pd.DataFrame:
    """Loads the Hirlam data and cleans it for further processing"""
    #opening the data for hirlam predictions
    Hirlam = []
    Hirlam.append(pd.read_csv(path+'2018_hirlam_predictions.csv',';'))
    Hirlam.append(pd.read_csv(path+'2019_hirlam_predictions.csv',','))
    Hirlam.append(pd.read_csv(path+'2020_hirlam_predictions.csv',','))
    Hirlam = pd.concat(Hirlam)
    
    #removing errors
    Hirlam = Hirlam[Hirlam['Prediction']>-2]
    return Hirlam


def loadActualData(path:str)->pd.DataFrame:
    """Loads and processes the actual data

    path is folder with all the actual files inside it."""    
    actualfiles = os.listdir(os.getcwd()+path)
    actual = []
    for file in actualfiles:
        actual.append(pd.read_csv(path+'/'+file,skiprows =2))
    actual = pd.concat(actual)
        
    
    actual['Begin'] = pd.to_datetime(actual['Begin'],dayfirst=True)
    actual_hrs = actual.resample('H',on='Begin').sum()
    actual_hrs['total'] =actual_hrs.loc[:,list(actual_hrs.columns)[1:433]].sum(axis=1)
    actual_hrs['avg'] =actual_hrs['total']/len(list(actual_hrs.columns)[1:433])
    return actual_hrs



def hourpreds(data: pd.DataFrame)->list:
    """Turns prediction dataframe into lists of dataframes based on
    difference between time of prediction and actual time."""
    #sets columns to datetime format
    data['ModelDate'] = pd.to_datetime(data['ModelDate'],format='%Y-%m-%d %H',exact=True)
    data['Time'] = pd.to_datetime(data['Time'],format='%Y-%m-%d %H',exact=True)
    
    #gets distance between time model made and actual time
    data['tdiff'] = data['Time']-data['ModelDate']
    
    #creates bins in 6H intervals to put the data in (predictions are done every 6H)
    intervalues = pd.timedelta_range(start='0',freq='6H', periods = 10)
    intervals= []
    for n in range(len(intervalues)-1):
        intervals.append(pd.Interval(left=intervalues[n],right=intervalues[n+1],closed='left'))
    interindex = pd.IntervalIndex(intervals)
    
    #puts data into respective bins
    data['measurepoint'] = pd.cut(data['tdiff'],bins=interindex)
    
    ####################################
    data_datediff = data.groupby(data['measurepoint'])
    
    frames = []
    for group in data_datediff:
        group = group[1].reset_index().drop('index',axis=1)
        frames.append(pd.DataFrame(group))
    return frames

 

def getTheRainfallData(pathPred:str,pathActual:str)->pd.DataFrame:
    """Matches the predictions and actual data on time of rainfall.
    Needs paths from wd to both place with 6 prediction csv and with the folder of actual data"""

    #get prediction data
    pred_harmonie = hourpreds(loadHarmonieData(pathPred))
    pred_hirlam = hourpreds(loadHirlamData(pathPred))
    #get actual data
    actual_data = loadActualData(pathActual)
    
    #create dataframe to put predictions into
    preds = pd.DataFrame()
    preds[['Time','actual']] = actual_data.reset_index()[['Begin','avg']]
    preds['Time'] = pd.to_datetime(preds['Time'],format='%Y-%m-%d %H',exact=True)

    #match predictions to actual data on Time of rainfall
    for frame in pred_hirlam:
        frame[f'hirlam_pred {frame["tdiff"][0]}'] = frame['Prediction']
        preds = preds.merge(frame[['Time',f'hirlam_pred {frame["measurepoint"][0]}']],on='Time',how='left')
    for frame in pred_harmonie:
        frame[f'harmonie_pred {frame["tdiff"][0]}'] = frame['Prediction']
        preds = preds.merge(frame[['Time',f'harmonie_pred {frame["measurepoint"][0]}']],on='Time',how='left')
    return preds



if name == "main":
    getTheRainfallData(pathPred = 'rainfall/rainfall/',pathActual = 'rainfall/rainfall/rain_timeseries')

