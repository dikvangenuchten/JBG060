import pandas as pd
import matplotlib.pyplot as plt


def FalseNegPlot(rainfallPredictions: pd.DataFrame, save_as: str):
    """Plots the false negatives and saves to saveas"""
    if 'Unnamed: 0' in rainfallPredictions.columns:
        rainfallPredictions = rainfallPredictions.drop('Unnamed: 0', axis=1)
    selection = []
    for series in rainfallPredictions.drop(['Time', 'actual'], axis=1).columns:
        selection.append([series, len(rainfallPredictions[series][(rainfallPredictions['actual'] > 0.35) & (
                    rainfallPredictions[series] < 0.35)]) / len(rainfallPredictions[series].dropna())])
    select_as_fraq = pd.DataFrame(selection)
    select_as_fraq[1] = select_as_fraq[1] / (
                len(rainfallPredictions['actual'][rainfallPredictions['actual'] > 0.35]) / len(
            rainfallPredictions['actual'])) * 100
    select_as_fraq[2] = ['hirlam: 0d 0-6h', 'hirlam: 0d 6-12h', 'hirlam: 0d 12-18h', 'hirlam: 0d 18-24h',
                         'hirlam: 1d 0-6h', 'hirlam: 1d 6-12h', 'hirlam: 1d 12-18h', 'hirlam: 1d 18-24h',
                         'hirlam: 2d 0-6h', 'harmonie: 0d 0-6h', 'harmonie: 0d 6-12h', 'harmonie: 0d 12-18h',
                         'harmonie: 0d 18-24h', 'harmonie: 1d 0-6h', 'harmonie: 1d 6-12h', 'harmonie: 1d 12-18h',
                         'harmonie: 1d 18-24h', 'harmonie: 2d 0-6h']

    plt.barh(y=select_as_fraq[2], width=select_as_fraq[1], color='#C60F0F')
    plt.title('% Of data with rain>0.35mm/h but \n prediction<0.35mm/h', size=18)
    plt.ylabel('prediction model: hours in advance', size=14)
    plt.xlabel('% of false negatives', size=14)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.tick_params(axis='both', which='minor', labelsize=12)
    plt.grid(axis='x', linestyle='--')
    plt.savefig(f'{save_as}', bbox_inches='tight', dpi=1000)
    return plt.show()


def diffPropPlot(rainfallPredictions: pd.DataFrame, save_as: str):
    """Plots the proportion of large differences saves to saveas"""
    if 'Unnamed: 0' in rainfallPredictions.columns:
        rainfallPredictions = rainfallPredictions.drop('Unnamed: 0', axis=1)
    diffProp = []
    for series in rainfallPredictions.drop(['Time', 'actual'], axis=1).columns:
        diffProp.append([series, len(
            rainfallPredictions[series][(rainfallPredictions['actual'] - rainfallPredictions[series]) > 0.1]) / len(
            rainfallPredictions[series].dropna())])
    diffProp = pd.DataFrame(diffProp)
    diffProp[1] = diffProp[1] * 100
    diffProp[2] = ['hirlam: 0d 0-6h', 'hirlam: 0d 6-12h', 'hirlam: 0d 12-18h', 'hirlam: 0d 18-24h', 'hirlam: 1d 0-6h',
                   'hirlam: 1d 6-12h', 'hirlam: 1d 12-18h', 'hirlam: 1d 18-24h', 'hirlam: 2d 0-6h', 'harmonie: 0d 0-6h',
                   'harmonie: 0d 6-12h', 'harmonie: 0d 12-18h', 'harmonie: 0d 18-24h', 'harmonie: 1d 0-6h',
                   'harmonie: 1d 6-12h', 'harmonie: 1d 12-18h', 'harmonie: 1d 18-24h', 'harmonie: 2d 0-6h']

    plt.barh(y=diffProp[2], width=diffProp[1], color='#C60F0F')
    plt.title('% Of data with 0.1mm/h+ of prediction error', size=18)
    plt.ylabel('prediction model: hours in advance', size=14)
    plt.xlabel('% of large differences', size=14)
    plt.grid(axis='x', linestyle='--')
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.tick_params(axis='both', which='minor', labelsize=12)
    plt.savefig(f'{save_as}', bbox_inches='tight', dpi=1000)
    return plt.show()
