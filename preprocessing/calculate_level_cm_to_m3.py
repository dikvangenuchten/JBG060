import pandas as pd
import numpy as np

def calculate_single_cm_to_m3(pump):
    inflow_df = pd.read_csv(f"processed\\pump_in_flow_appr_{pump}.csv")

    # Calculate the difference in pump water volume, so calculating how much water causes the difference
    inflow_df['in_minus_out'] = abs(inflow_df['flow_in'] - inflow_df['hstWaarde'])
    inflow_df['level'] = inflow_df.iloc[:, 1].round()
    inflow_df['prev_level'] = inflow_df['level'].shift(1)

    # Creating a n x m dataframe for the data
    indexes = np.array(inflow_df['level'].min() + np.arange(inflow_df['level'].max() - inflow_df['level'].min()))
    columns = np.array(inflow_df['level'].min() + np.arange(inflow_df['level'].max() - inflow_df['level'].min()))
    df = pd.DataFrame(0, index=indexes, columns=columns)

    # We fill this dataframe with the mean of all corresponding data belonging to every single cell
    mean_df = inflow_df.groupby(['level', 'prev_level']).mean().reset_index()
    mean_df['rounded_level_diff'] = abs(mean_df['level'] - mean_df['prev_level'])
    mean_df.loc[mean_df['rounded_level_diff'] == 0, 'rounded_level_diff'] = 1
    mean_df = mean_df.loc[mean_df['level'] != mean_df['prev_level']]
    mean_df['mean_in_minus_out_per_cm'] = mean_df['in_minus_out'] / mean_df['rounded_level_diff']
    mean_df = mean_df.groupby(['prev_level']).mean().reset_index()
    resulting_df = pd.DataFrame(columns=['cm', 'm3'])
    resulting_df['cm'] = mean_df['prev_level']
    resulting_df['m3'] = mean_df['mean_in_minus_out_per_cm'].fillna(0).cumsum()
    print("Pump done!")
    return resulting_df
