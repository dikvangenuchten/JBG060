import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

#emmie Code
#andere zou ook moeten werken
def split_date_column(df, column: str):
    '''Takes a dataframe and the column in which a date can be found,
    converts this date into a datetime object, and then splits the object
    into year, month, and date columns.'''

    # Format each row in the 'Time' column into a datetime object
    df['Year'] = pd.DatetimeIndex(df[column]).year
    df['Month'] = pd.DatetimeIndex(df[column]).month
    df['Day'] = pd.DatetimeIndex(df[column]).day

    return df


def create_test_data(df, final_days: int):
    '''Takes a dataframe with split date columns and creates test data in the
    following way: for every month, take the last 7 consecutive days.'''

    # Drop the 2017 entry (should be in training)
    df = df.drop(df[df['Year'] == 2017].index)

    # Filter out the final month, because this month is not complete
    final_month = df[(df['Year'] == 2020) & (df['Month'] == 8)]
    final_month_n = ((final_days - 5)) * 24 + 22  # 5 missing days, 1 with 22 hours
    test_final_month = final_month.tail(final_month_n)

    # Drop the final month and create groups, then take the n last days
    df_no_final = df.drop(final_month.index)
    month_groups = df_no_final.groupby(['Year', 'Month'])
    test_other = month_groups.tail(final_days * 24)

    # Concat final month with the other months
    test_data = pd.concat([test_other, test_final_month])

    return test_data


def create_train_data(df, test_df):
    '''Creates the training data by removing the rows that are already
    in the test dataframe made by the create_test_data function.'''

    indexed_test_data = test_df.reset_index()
    index_list = indexed_test_data['index'].tolist()
    train_data = df.drop(index_list)

    return train_data
#einde emmie code


#nieuwe code
def prepDataForPlot(train_data:pd.DataFrame,test_data:pd.DataFrame)->list:
    '''Readies the data for plotting by removing unnecessairy columns and binning the rainfall into three categories '''
    
    #places desired items in bins
    for model in test_data.drop(['Unnamed: 0','Time','Year','Month','Day'],axis=1).columns:
        test_data[model] = pd.cut(test_data[model],
                                  bins=[-float("inf"),0.35,0.7,float("inf")],
                                  labels=['No rain','medium rain','heavy rain'], 
                                  ordered=False)
        train_data[model]=pd.cut(train_data[model],
                                  bins=[-float("inf"),0.35,0.7,float("inf")],
                                  labels=['No rain','medium rain','heavy rain'], 
                                  ordered=False)
        
    #removes unnecessairy data and turns remaining data into a plottable form
    sparse_train_data = train_data.drop(['Unnamed: 0','Time','Year','Month','Day'],axis=1)
    sparse_test_data = test_data.drop(['Unnamed: 0','Time','Year','Month','Day'],axis=1)
    counts_train = sparse_train_data.apply(lambda x: x.value_counts() / len(x.dropna())).transpose()
    counts_test = sparse_test_data.apply(lambda x: x.value_counts() / len(x.dropna())).transpose()
    
    #turns the categorical index into a normal one so index can be changed
    counts_train.columns = counts_train.columns.astype('str')
    counts_test.columns = counts_test.columns.astype('str')
    
    #renames index to save space
    counts_train.index = ['actual','hi 0-6h','hi 6-12h','hi 12-18h','hi 18-24h','hi 1d 0-6h', 'hi 1d 6-12h','hi 1d 12-18h','hi 1d 18-24','hi 2d 0-6h','ha 0-6h','ha 6-12h','ha 12-18h','ha 18-24h','ha 1d 0-6h', 'ha 1d 6-12h','ha 1d 12-18h','ha 1d 18-24','ha 2d 0-6h']
    counts_test.index  = ['actual','hi 0-6h','hi 6-12h','hi 12-18h','hi 18-24h','hi 1d 0-6h', 'hi 1d 6-12h','hi 1d 12-18h','hi 1d 18-24','hi 2d 0-6h','ha 0-6h','ha 6-12h','ha 12-18h','ha 18-24h','ha 1d 0-6h', 'ha 1d 6-12h','ha 1d 12-18h','ha 1d 18-24','ha 2d 0-6h']
    
    #multiplies by 100 to get percentages instead of fractions
    counts_train = counts_train.multiply(100)
    counts_test = counts_test.multiply(100)
    return [counts_train,counts_test]


#plotting function stolen from stackoverflow and edited a bit
#stolen from: https://stackoverflow.com/questions/22787209/how-to-have-clusters-of-stacked-bars-with-python-pandas
def plot_clustered_stacked(dfall, labels=None, title="multiple stacked bar plot",  H="/", **kwargs):
    """Given a list of dataframes, with identical columns and index, create a clustered stacked bar plot. 
labels is a list of the names of the dataframe, used for the legend
title is a string for the title of the plot
H is the hatch used for identification of the different dataframe"""

    n_df = len(dfall)
    n_col = len(dfall[0].columns) 
    n_ind = len(dfall[0].index)
    axe = plt.subplot(111)

    for df in dfall : # for each data frame
        axe = df.plot(kind="bar",
                      linewidth=0,
                      stacked=True,
                      ax=axe,
                      legend=False,
                      grid=False,
                      **kwargs)  # make bar plots

    h,l = axe.get_legend_handles_labels() # get the handles we want to modify
    for i in range(0, n_df * n_col, n_col): # len(h) = n_col * n_df
        for j, pa in enumerate(h[i:i+n_col]):
            for rect in pa.patches: # for each index
                rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col))
                rect.set_hatch(H * int(i / n_col)) #edited part     
                rect.set_width(1 / float(n_df + 1))

    axe.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    axe.set_xticklabels(df.index, rotation = 90)
    axe.set_title(title)
    fmt = '{x}%'
    tick = mtick.StrMethodFormatter(fmt)
    axe.yaxis.set_major_formatter(tick) 
    # Add invisible data to add another legend
    n=[]        
    for i in range(n_df):
        n.append(axe.bar(0, 0, color="gray", hatch=H * i))

    l1 = axe.legend(h[:n_col], l[:n_col], loc=[1.01, 0.5])
    if labels is not None:
        l2 = plt.legend(n, labels, loc=[1.01, 0.1]) 
    axe.add_artist(l1)
    return axe

if __name__=="__main__":
    rainfall_data = pd.read_csv('rainfallpredictionsHourlyV3.csv')
    new_rainfall_data = split_date_column(rainfall_data, 'Time')
    test_data = create_test_data(new_rainfall_data, 7)
    train_data = create_train_data(new_rainfall_data, test_data)
    plot_clustered_stacked(prepDataForPlot(train_data,test_data),["train","test"],'Composition of train and test data for all rainfall models')
    plt.show()