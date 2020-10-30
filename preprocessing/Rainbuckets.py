def make_rain_buckets(df, rain_col_name):
    '''Adds rainfall buckets to a df, needs the df and the col_name of the rainfall data as input'''

    rainfall_list = df[rain_col_name].values.tolist()

    hourlist_no_rainfall = []
    hourlist_medium_rainfall = []
    hourlist_heavy_rainfall = []

    daylist_no_rainfall = []
    daylist_small_rainfall = []
    daylist_medium_rainfall = []
    daylist_heavy_rainfall = []

    for i in range(0, len(rainfall_list)):
        if i % 24 == 0:

            if i + 24 < len(rainfall_list):
                daily_rain = sum(rainfall_list[i:i+24])
                a = 24
            else:
                daily_rain = sum(rainfall_list[i:])
                a = len(rainfall_list) - i

            if daily_rain < 0.5:
                for j in range(0, a):
                    daylist_no_rainfall.append(1)
                    daylist_small_rainfall.append(0)
                    daylist_medium_rainfall.append(0)
                    daylist_heavy_rainfall.append(0)

            elif daily_rain < 10:
                for j in range(0, a):
                    daylist_no_rainfall.append(0)
                    daylist_small_rainfall.append(1)
                    daylist_medium_rainfall.append(0)
                    daylist_heavy_rainfall.append(0)

            elif daily_rain < 20:
                for j in range(0, a):
                    daylist_no_rainfall.append(0)
                    daylist_small_rainfall.append(0)
                    daylist_medium_rainfall.append(1)
                    daylist_heavy_rainfall.append(0)

            else:
                for j in range(0, a):
                    daylist_no_rainfall.append(0)
                    daylist_small_rainfall.append(0)
                    daylist_medium_rainfall.append(0)
                    daylist_heavy_rainfall.append(1)

        hourly_rain = rainfall_list[i]

        if hourly_rain < 0.35:
            hourlist_no_rainfall.append(1)
            hourlist_medium_rainfall.append(0)
            hourlist_heavy_rainfall.append(0)

        elif hourly_rain < 0.7:
            hourlist_no_rainfall.append(0)
            hourlist_medium_rainfall.append(1)
            hourlist_heavy_rainfall.append(0)

        else:
            hourlist_no_rainfall.append(0)
            hourlist_medium_rainfall.append(0)
            hourlist_heavy_rainfall.append(1)

    df['hourly_rain_none'] = hourlist_no_rainfall
    df['hourly_rain_medium'] = hourlist_medium_rainfall
    df['hourly_rain_heavy'] = hourlist_heavy_rainfall

    df['daily_rain_none'] = daylist_no_rainfall
    df['daily_rain_small'] = daylist_small_rainfall
    df['daily_rain_medium'] = daylist_medium_rainfall
    df['daily_rain_heavy'] = daylist_heavy_rainfall
