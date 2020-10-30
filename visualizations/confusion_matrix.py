import pandas as pd

rainfall = pd.read_csv('rainfallpredictionsHourlyV1.csv')

actual_rain = rainfall['actual'].values.tolist()
pred_rain = rainfall['hirlam_pred 0 days 12:00:00'].values.tolist()

pred = []
actual = []

for i in range(0, len(actual_rain)):
    if actual_rain[i] < 0.35:
        actual.append('dry')
    elif actual_rain[i] >= 0.35:
        actual.append('wet')

    if pred_rain[i] >= 0.35:
        pred.append('wet')
    else:
        pred.append('dry')

y_actu = pd.Series(actual, name='Actual')
y_pred = pd.Series(pred, name='Predicted')
df_confusion = pd.crosstab(y_actu, y_pred)
df_conf_norm = df_confusion / len(pred)

print(df_conf_norm)