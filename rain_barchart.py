import matplotlib.pyplot as plt


def rain_stacked_bar_chart(df, time_col, path):
    """needs the dataframe and the column of the time as input, assumes you made the rain buckets with the
    make_rain_bucket function. Saves a bar chart to path"""
    time = df[time_col].values.tolist()
    change_index = [0]
    for i in range(0, len(time) - 1):
        if time[i][:7] != time[i + 1][:7]:
            change_index.append(i + 1)

    hourlist_no_rainfall = []
    hourlist_medium_rainfall = []
    hourlist_heavy_rainfall = []

    daylist_no_rainfall = []
    daylist_small_rainfall = []
    daylist_medium_rainfall = []
    daylist_heavy_rainfall = []

    for i in range(0, len(change_index) - 1):
        df2 = df[change_index[i]:change_index[i + 1]]

        hourlist_no_rainfall.append(df2['hourly_rain_none'].mean())
        hourlist_medium_rainfall.append(df2['hourly_rain_medium'].mean())
        hourlist_heavy_rainfall.append(df2['hourly_rain_heavy'].mean())

        daylist_no_rainfall.append(df2['daily_rain_none'].mean())
        daylist_small_rainfall.append(df2['daily_rain_small'].mean())
        daylist_medium_rainfall.append(df2['daily_rain_medium'].mean())
        daylist_heavy_rainfall.append(df2['daily_rain_heavy'].mean())

    # plot
    r = []
    for i in range(0, len(daylist_no_rainfall)):
        r.append(i)
    months = ['dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'jan', 'feb',
              'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may',
              'jun', 'jul']
    barwidth = 1

    # Create green Bars
    plt.bar(r, daylist_no_rainfall, color='#b5ffb9', edgecolor='white', width=barwidth)
    # Create orange Bars
    plt.bar(r, daylist_small_rainfall, bottom=daylist_no_rainfall, color='#f9bc86', edgecolor='white', width=barwidth)
    # Create blue Bars
    plt.bar(r, daylist_medium_rainfall, bottom=[i + j for i, j in zip(daylist_no_rainfall, daylist_small_rainfall)],
            color='#a3acff', edgecolor='white', width=barwidth)
    # Create black Bars
    plt.bar(r, daylist_heavy_rainfall,
            bottom=[i + j + k for i, j, k in zip(daylist_no_rainfall, daylist_small_rainfall, daylist_medium_rainfall)],
            color='black', edgecolor='white', width=barwidth)

    # Custom x axis
    plt.xticks(r, months)

    plt.savefig(path)
    # Show graphic
