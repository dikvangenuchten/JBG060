import pandas as pd

from visualizations.plot3a3bPoster import *
from visualizations.plot_8_9_11_poster import *
from visualizations.visualisations import *

if __name__ == '__main__':
    # datafile
    preds = pd.read_csv('RainfallPredictionsHourlyV3.csv')
    FalseNegPlot(preds, 'hand.png')
    diffPropPlot(preds, 'voet.png')

    # plot fig 8 and 9 poster
    # directory with pump model outputs
    direct = 'smart_sewage_multi_pump_dry_and_wet_with_lookahead\\' \
             'smart_sewage_multi_pump_dry_and_wet_with_lookahead\\'
    # range object
    dayrange = range(8137, 8161)
    # example
    MultiplotPredictions(directory=direct, hourrange=dayrange, smart=0, dry=1, howlong='day')

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

    figure2()
    figure4()
