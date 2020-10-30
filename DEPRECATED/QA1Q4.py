#required libraries
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

#######################
#rainfall Predictions:
#######################


#path to the rainfall folder:
path_pred = 'rainfall/rainfall/'


#opening the data for harmonie predictions (only predicts juli-august)
Harmonie= []
Harmonie.append(pd.read_csv(path_pred+'2018_harmonie_juli_augustus_predictions.csv',';'))
Harmonie.append(pd.read_csv(path_pred+'2019_harmonie_juli_augustus_predictions.csv',','))
Harmonie.append(pd.read_csv(path_pred+'2020_harmonie_juli_augustus_predictions.csv',','))
Harmonie = pd.concat(Harmonie)

#removing errors
Harmonie = Harmonie.replace(float(-9999.0),np.nan)
#implementing averages
predsonly = Harmonie.drop(['ModelDate','Time'],axis=1)
Harmonie['avg'] = predsonly.sum(axis=1)/len(predsonly.columns)

#Setting inline
Harmonie = Harmonie[['ModelDate','Time','avg']]

#############################


#opening the data for hirlam predictions
Hirlam = []
Hirlam.append(pd.read_csv(path_pred+'2018_hirlam_predictions.csv',';'))
Hirlam.append(pd.read_csv(path_pred+'2019_hirlam_predictions.csv',','))
Hirlam.append(pd.read_csv(path_pred+'2020_hirlam_predictions.csv',','))
Hirlam = pd.concat(Hirlam)

#removing errors
Hirlam = Hirlam.replace(float(-9999.0),np.nan)


#############################

#processes prediction data from hourly to dayly
def getRainfallPredictions(data: pd.DataFrame)->list:
    #str to datetime conversions
    data['ModelDate'] = pd.to_datetime(data['ModelDate'],format='%Y-%m-%d %H',exact=True)
    data['Time'] = pd.to_datetime(data['Time'],format='%Y-%m-%d %H',exact=True)
    #calculate x hour in advance prediction
    data['tdiff'] = data['ModelDate'] - data['Time'].dt.normalize()
    
    #sort by individual predictions
    data_datediff = data.groupby(data['tdiff'])
    
    
    frames = []
    #do in dayly insead of hourly
    #separates by difference in time between model creation and prediction time
    for diff in data_datediff:
        data_day = []
        #generates a new row for the entire day from all the hourly predictions
        for group in diff[1].groupby(diff[1]['Time'].dt.normalize()):
            newline = group[1].sum(axis=0)
            newline['tdiff'] = abs(newline['tdiff']/len(group[1])-pd.Timedelta(hours=18))
            newline['Time'] = group[0]
            data_day.append(newline)
        frames.append(pd.DataFrame(data_day))
    #list of dataframes with one frame per model prediction (e.g. made 1d12h or 2d before)
    return frames

#################################
#get predictions
pred_harmonie = getRainfallPredictions(Harmonie)
pred_hirlam = getRainfallPredictions(Hirlam)
#################################
print('predicting finished')

############
#actual data
############

path_actual_data = '\\rainfall\\rainfall\\rain_timeseries'

#loading data
actualfiles = os.listdir(os.getcwd()+path_actual_data)
actual = []
for file in actualfiles:
    actual.append(pd.read_csv('rainfall/rainfall/rain_timeseries/'+file,skiprows =2))
actual = pd.concat(actual)

################

#making datetimes
actual['Begin'] = pd.to_datetime(actual['Begin'],dayfirst=True)

#sorting and cleaning
actual = actual.sort_values(by='Begin')
actual = actual.reset_index()
actual = actual.drop(['index'],axis=1)


#converting to days (takes an assload of time)
actual_days = []
for group in actual.groupby(actual['Begin'].dt.normalize()):

    newline = group[1].sum(axis=0)
    newline['Begin'] = group[0]
    newline['Eind'] = newline['Eind'][-19:]
    actual_days.append(newline)
actual_days = pd.DataFrame(actual_days)

#getting the avg daily rain
actual_days['total'] =actual_days.loc[:,list(actual_days.columns)[3:436]].sum(axis=1)
actual_days['avg'] =actual_days['total']/len(list(actual_days.columns)[3:436])
print('actual data finished')


###################################
#Complete dataframe for predictions
###################################

#renaming as preparation for mergers
preds = pd.DataFrame()
preds[['Time','actual']] = actual_days[['Begin','avg']]

#merging the frames 
for frame in pred_hirlam:
    frame[f'hirlam_pred {frame["tdiff"][0]}'] = frame['Prediction']
    preds = preds.merge(frame[['Time',f'hirlam_pred {frame["tdiff"][0]}']],on='Time',how='left')
for frame in pred_harmonie:
    frame[f'harmonie_pred {frame["tdiff"][0]}'] = frame['avg']
    preds = preds.merge(frame[['Time',f'harmonie_pred {frame["tdiff"][0]}']],on='Time',how='left')

#dataframe is: "preds"
print('all finished')


#OPTIONAL, plots for Q&A 1 Q4

#plots 1
"""
#comment out line 44 for other plot
plt.bar(height=pred_hirlam[10]['Prediction'],x=pred_hirlam[10]['Time'],width=5)
plt.show()
"""

#plot 2
"""
corrs = []
for series in preds.drop(['Time','actual'],axis=1).columns:
    corrs.append([series,preds['actual'].corr(preds[series], method='pearson')])
corrs = pd.DataFrame(corrs)


plt.figure(figsize=(10,5))
plt.barh(y=corrs[0],width=corrs[1])
plt.show()
"""

#plot 3
"""
voet = []
for series in preds.drop(['Time','actual'],axis=1).columns:
    voet.append([series,len(preds[series][abs(preds['actual']-preds[series])>6])/len(preds[series].dropna())])
oversixv = pd.DataFrame(voet)
plt.barh(y=oversixv[0],width=oversixv[1])
plt.show()
"""

#plot 4
"""
krant = []
for series in preds.drop(['Time','actual'],axis=1).columns:
    krant.append([series, len(preds[series][(preds['actual']>7) & (preds[series]<5)])/len(preds[series].dropna())])
meerkrant = pd.DataFrame(krant)
plt.barh(y=meerkrant[0],width=meerkrant[1])
plt.show()
"""