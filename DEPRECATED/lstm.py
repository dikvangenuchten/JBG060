import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM
import os

# Keep in mind, this file is far from finished
def create_model():
    df = pd.read_csv(os.path.join('preprocessing', 'processed', 'data_rainfall_2018_harmonie_juli_augustus_predictions.csv'));
    train_test_split_pred = len(df) - round(len(df)/8)
    trainX = df[:train_test_split_pred]
    testX = df[(train_test_split_pred - 1):]

    df = pd.read_csv(os.path.join('preprocessing', 'processed', 'data_sewer_data_db_data_pump_level__03-09-2019_16_46_.csv'));
    train_test_split_level = len(df) - round(len(df)/8)
    trainY = df[:train_test_split_level]
    testY = df[(train_test_split_level - 1):]

    # Creating model
    hidden_size = 4
    model = Sequential()
    model.add(LSTM(hidden_size, return_sequences=True))
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mean_squared_error'])


    # Training model
    model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2)

    # Testing model
    prediction = model.predict(testX)
    error = abs(prediction - testY)

