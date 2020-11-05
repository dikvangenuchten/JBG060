import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np


# Figure 8 and 9 for poster
def MultiplotPredictions(directory: str, hour_range: range, smart: bool = 1, dry: bool = 1, howlong: str = 'day') -> str:
    """Plots the model results on a certain range of hours.
    directory:str = directory with model results on the different pumping stations
    hourrange:range = a range of hours to plot (e.g. range(8000:8168) for one week from hour 8000 to 8168)
    smart:bool = indicate if the directory contains the smart model or the naive model, 1=smart, default is 1
    dry:bool = indicate if the timerange is mainly dry or wet, 1=dry, default is 1
    timerange:str = indicate the range over which the plot is run, (e.g. day,week,fortnight,month etc.), default is day, (corresponding of hourrange of length 24)
    """
    if dry == 1:
        weather = 'Dry'
    else:
        weather = 'Wet'
    if smart == 1:
        model = 'Smart'
    else:
        model = 'Naive'

    actualfiles = os.listdir(directory)
    for file in actualfiles:
        if file == 'complete_sewage_system.csv':
            pass
        else:
            actual = pd.read_csv(directory + file)
            # if fixed for old model remove this
            if model == 0:
                actual = actual.drop([i for i in range(len(actual)) if i % 2 == 1]).reset_index().drop('index', axis=1)
            plank = actual[actual['Time'].astype(int).isin(list(hour_range))]
            plank['TTime'] = list(range(len(plank['Time'])))
            plt.plot(plank['TTime'], plank['Predicted Wet Inflow'].astype(float), color='#81A4CD', linewidth=5)
            plt.plot(plank['TTime'], plank['Predicted Dry Inflow'].astype(float), color='#054A91', linewidth=5)
            plt.plot(plank['TTime'], plank['Actual Inflow'].astype(float), color='#C60F0F', linewidth=5)
            plt.title(f'{model} Inflow Prediction {file[:-4]} On A {weather} {howlong}', size=18)
            plt.ylabel('Inflow in $m^3$', size=14)
            plt.xlabel('Time in hours', size=14)
            plt.tick_params(axis='both', which='major', labelsize=12)
            plt.tick_params(axis='both', which='minor', labelsize=12)
            plt.legend(['Predicted Wet Inflow', 'Predicted Dry Inflow', 'Approximated Actual Inflow'])
            plt.savefig(f'Inflow_{weather}_{howlong}_{model}_{file}.png', bbox_inches='tight', dpi=1000)
            plt.show()
    return 'done'


def PlotModelComparison(old: pd.DataFrame, new: pd.DataFrame, hourrange: range = None, deriv: bool = 1):
    """Plots the difference between old and new model
    
    old:pd.DataFrame = data from the old Aa en Maas Model
    new:pd.DataFrame =  data from the new Bayesian optimization model
    hourrange:range =  a  range from where to where to plot, most ~1 week of data (range of 168 hours) is recommended to keep the data readable
    deriv:bool = if you want the original data or the 1st derivative of the data, 1= derivative of the data.
    """
    # some Prepping
    old['Total Outflow'] = old['Total Outflow'].astype(float)
    new['Total Outflow'] = new['Total Outflow'].astype(float)
    old['Time'] = old['Time'].astype(int)
    new['Time'] = new['Time'].astype(int)
    a = [new['Total Outflow'][i] - new['Total Outflow'][i - 1] for i in range(1, len(new))]
    a.insert(0, new['Total Outflow'][0])
    new['diff'] = a

    if hourrange:
        old = old[old['Time'].isin(list(hourrange))]
        new = new[new['Time'].isin(list(hourrange))]
    if deriv == 1:
        plt.plot(list(old['Time'])[:-1], np.diff(list(old['Total Outflow'])), color='#81A4CD', lw=3)
        plt.plot(list(new['Time'])[:-1], np.diff(list(new['diff'])), color='#C60F0F', lw=3)
        plt.plot(list(old['Time'])[:-1], [1000] * len(list(old['Time'])[:-1]), color='gray', linestyle='--', lw=2)
        plt.plot(list(old['Time'])[:-1], [-1000] * len(list(old['Time'])[:-1]), color='gray', linestyle='--', lw=2)
        derivTitle = 'Derivative of'
    elif deriv == 0:
        plt.plot(list(old['Time']), list(old['Total Outflow']), color='#81A4CD', lw=3)
        plt.plot(list(old['Time']), list(new['diff']), color='#C60F0F', lw=3)
        derivTitle = ''
    plt.title(f'{derivTitle} Outflow over Time', size=18)
    plt.ylabel('Outflow in $m^3$', size=14)
    plt.xlabel('Time in hours', size=14)
    plt.grid(axis='x', linestyle='--')
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.tick_params(axis='both', which='minor', labelsize=12)
    plt.legend(['Naive Aa-en-Maas Model', 'Proposed Model'], prop={'size': 12})
    if hourrange:
        plt.savefig(f'{derivTitle}_Outflow_over_Time_hours_{hourrange[0]}_to_{hourrange[-1]}.png', bbox_inches='tight',
                    dpi=1000)
    else:
        plt.savefig(f'{derivTitle}_Outflow_over_Time.png', bbox_inches='tight', dpi=1000)
    return plt.show()
