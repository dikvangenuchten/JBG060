import pandas as pd

from visualizations.plotsRainfallPoster3aLargePredictionErrors3bFalseNegatives import *
from visualizations.plot8And9_InflowPredictions_plot11_OutflowOverTime_poster import *
from visualizations.plot_5_pumps_level_to_m3 import *
from visualizations.visualisations import *


def visualization_main():
    # datafile
    preds = pd.read_csv('processed\\rainfallpredictionsHourly.csv')
    FalseNegPlot(preds, 'FalseNegatives.png')
    diffPropPlot(preds, 'DifferentProportions.png')

    # plot fig 8 and 9 poster
    # directory with pump model outputs
    direct = 'smart_sewage_multi_pump_dry_and_wet_with_lookahead\\' \
             'smart_sewage_multi_pump_dry_and_wet_with_lookahead\\'
    # range object
    dayrange = range(8137, 8161)
    # example
    MultiplotPredictions(directory=direct, hour_range=dayrange, smart=0, dry=1, howlong='day')

    # plot fig 11 poster
    old = pd.read_csv(
        'dumb_sewage_multi_pump_dry_and_wet\\'
        'dumb_sewage_multi_pump_dry_and_wet\\'
        'complete_sewage_system.csv')
    new = pd.read_csv(
        'smart_sewage_multi_pump_dry_and_wet_with_lookahead\\'
        'smart_sewage_multi_pump_dry_and_wet_with_lookahead\\'
        'complete_sewage_system.csv')
    # dropping repeating headers, if fixed remove this line
    old = old.drop([i for i in range(len(old)) if i % 2 == 1]).reset_index().drop('index', axis=1)
    # example
    PlotModelComparison(old, new, range(8000, 8168), deriv=0)

    # Plots the 5 pumps and their level in cm at one axis, with the m3 till that level at the other axis
    plot_5_pumps_level_to_m3()

    # TODO explain
    figure2()
    figure4()


if __name__ == '__main__':
    visualization_main()
