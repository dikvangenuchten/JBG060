import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.pyplot import figure

path = 'data preparation'
def append_col(df1, df2, append_colname, index_colname1, index_colname2, new_colname):
    '''Appends append_colname from df2 to df1 with new_colname as name; compares the values in index_colname1 and
    index_colname2 to decide where to add which values. Adds None if it cant find a value index_colname1 in
    index_colname2'''

    append_list = []

    for value in df1[index_colname1].values.tolist():

        try:
            append_list.append(df2[df2[index_colname2] == value][append_colname].values[0])
        except IndexError:
            append_list.append(None)

    df1[new_colname] = append_list

    print(append_colname + ' appended as ' + new_colname)

def figure2(path = path, begin_date =' 2018-04-29', end_date = '2018-04-30'):

    # read data and combine rainfall with flow/level
    helftheuvel1uur = pd.read_csv(f'{path}/helftheuvel.csv')
    helftheuvel1uur = helftheuvel1uur.rename(columns={'Unnamed: 0': 'Date'})
    helftheuvel1uur['Date'] = pd.to_datetime(helftheuvel1uur['Date'])

    rainfall = pd.read_csv('rainfallpredictionsHourlyV3.csv')
    rainfall = rainfall.rename(columns={'Time': 'Date'})
    rainfall['Date'] = pd.to_datetime(rainfall['Date'])

    total = pd.merge(helftheuvel1uur, rainfall, on='Date')
    total = total[['Date', '003: Helftheuvelweg Niveau (cm)', 'hstWaarde', 'actual',
                   'hirlam_pred [0 days 18:00:00, 1 days 00:00:00)']]
    total['Date'] = pd.to_datetime(total['Date'])
    total.set_index('Date', inplace=True)

    # read 1 minute data
    helftheuvel1min = pd.read_csv(f'{path}/helftheuvel1min.csv')
    helftheuvel1min = helftheuvel1min.rename(columns={'Unnamed: 0': 'Date'})
    helftheuvel1min['Date'] = pd.to_datetime(helftheuvel1min['Date'])
    helftheuvel1min.set_index('Date', inplace=True)


    # Plot for level and rainfall
    # set timespan for plot
    date = begin_date
    end = end_date
    helftheuvel2 = total[date:end]

    y = helftheuvel2.index
    fig, ax1 = plt.subplots(figsize=(8, 8))

    # Level
    color = 'tab:red'
    ax1.set_xlabel('time (hours)', fontsize=16)
    ax1.set_ylabel('level (cm)', color=color, fontsize=16)
    p1, = ax1.plot(y, helftheuvel2['003: Helftheuvelweg Niveau (cm)'], color=color, label='level')
    ax1.tick_params(axis='y', labelcolor=color, labelsize=14)
    ax1.tick_params(axis='x', rotation=10, labelsize=11)
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d '))

    # Rainfall
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Rainfal (mm)', color=color, fontsize=16)  # we already handled the x-label with ax1
    p2, = ax2.plot(y, helftheuvel2['actual'], color=color, label='Rainfall')

    ax2.tick_params(axis='y', labelcolor=color, labelsize=14)
    ax2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))

    lst = [p1, p2]
    plt.title('Rain and level for helftheuvel pump ', fontsize=18)
    ax1.legend(lst, [l.get_label() for l in lst], loc=2, fontsize='x-large')

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.savefig('rain_level_helft_last.png', dpi=1000)
    plt.show()

def figure4(path = path, begin_date = '2018-12-01', end_date = '2018-12-10'):
    helftheuvel1uur = pd.read_csv(f'{path}/helftheuvel.csv')
    helftheuvel1uur = helftheuvel1uur.rename(columns={'Unnamed: 0': 'Date'})
    helftheuvel1uur['Date'] = pd.to_datetime(helftheuvel1uur['Date'])

    rainfall = pd.read_csv('rainfallpredictionsHourlyV3.csv')
    rainfall = rainfall.rename(columns={'Time': 'Date'})
    rainfall['Date'] = pd.to_datetime(rainfall['Date'])

    total = pd.merge(helftheuvel1uur, rainfall, on='Date')
    total = total[['Date', '003: Helftheuvelweg Niveau (cm)', 'hstWaarde', 'actual',
                   'hirlam_pred [0 days 18:00:00, 1 days 00:00:00)']]
    total['Date'] = pd.to_datetime(total['Date'])
    total.set_index('Date', inplace=True)

    # Plot with flow, predicted and actual rainfall
    figure(figsize=(15, 6))
    date = begin_date
    end = end_date
    data = total[date:end]

    ax = plt.gca()
    ax.set_title('Rainfall and flow for helftheuvel pump December 2018', fontsize=20)
    # rainfall
    x = data.index
    y = data['actual']
    color = 'tab:red'
    p1, = ax.plot(x, y, label='actual rainfall', color=color)
    ax.set_xlabel('Date', fontsize=15)
    ax.set_ylabel('rainfall (mm)', fontsize=15, color=color)
    ax.tick_params(axis='y', labelcolor=color, labelsize=14)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%a %Y-%m-%d'))
    ax.tick_params(axis='x', rotation=10, labelsize=14)
    ax.set_ylim(-5, 10)
    # predicted rainfall
    y = data['hirlam_pred [0 days 18:00:00, 1 days 00:00:00)']
    color = 'tab:green'
    p3, = ax.plot(x, y, label='predicted rainfall', color=color)
    # flow
    ax1 = ax.twinx()
    color = 'tab:blue'
    y = data['hstWaarde']
    p2, = ax1.plot(x, y, label='flow', color=color, alpha=0.8)
    ax1.set_ylabel('Flow (m3/h)', fontsize=15, color=color)
    ax1.tick_params(axis='y', labelcolor=color, labelsize=14)
    ax1.tick_params(axis='x', rotation=10, labelsize=14)
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%a %Y-%m-%d'))

    lst = [p1, p2, p3]
    ax.legend(lst, [l.get_label() for l in lst], loc=1, fontsize='x-large')

    plt.savefig('(predicted)rainfall_flow_helftheuvel_last.png', bbox_inches='tight', dpi=1000)
    plt.show()



figure2()
figure4()