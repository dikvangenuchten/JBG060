import pandas as pd


def split_weeks(df, train_weeks: int, test_weeks: int):
    '''Splits the given dataframe into n given training weeks and m given
    testing weeks (all consecutive). Right now this function assumes that your
    data starts on a MONDAY!!'''

    # Create a separate index column and converts this to a list
    indexed_df = df.reset_index()
    index_list = indexed_df['index'].tolist()

    # Split the index list into subsets based on the total interval in days
    train_interval = train_weeks * (7 * 24)
    total_interval = (train_weeks + test_weeks) * (7 * 24)
    intervals = [index_list[x: x + total_interval] for x in range(0, len(index_list), total_interval)]

    # Set train and test data both to the current dataset
    train_df = df
    test_df = df

    # Create train dataset by dropping the last two weeks of every interval (keeping the first 8 weeks)
    for i in intervals:
        test_index = i[train_interval:]
        train_df = train_df.drop(test_index)

    # Create test dataset by dropping the first eight weeks of each interval (keeping the last 2 weeks)
    for j in intervals:
        train_index = j[:train_interval]
        test_df = test_df.drop(train_index)

    return train_df, test_df


if __name__ == '__main__':
    rainfall_data = pd.read_csv('rainfallpredictions1_1.csv')
    train_data, test_data = split_weeks(rainfall_data, 8, 2)
