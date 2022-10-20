# -*- coding: utf-8 -*-
"""Time Series_Regina.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZSpwLZ7uDYaz6-U_py5VUYggV7DI6qOc

##Project 2: Time Series
"""

import numpy as np
import pandas as pd
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

train = pd.read_csv('/content/drive/MyDrive/DATA/daily-max-temperatures.csv')
train.head()

train.describe

train.isnull().sum()

train['Temperature'] = train['Temperature'].astype(float)

dates = train['Date'].values
temp  = train['Temperature'].values
 
plt.figure(figsize=(15,5))
plt.plot(dates, temp)
plt.title('Daily Max Temperature',
          fontsize=20);

date_temp, date_test, temp_train, temp_test  = train_test_split(dates, temp, test_size=0.2, shuffle=False)

def windowed(series, window_size, batch_size, shuffle_buffer):
  series = tf.expand_dims(series, axis=1)
  ds = tf.data.Dataset.from_tensor_slices(series)
  ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
  ds = ds.flat_map(lambda w: w.batch(window_size + 1))
  ds = ds.shuffle(shuffle_buffer)
  ds = ds.map(lambda w: (w[:-1], w[-1:]))
  return ds.batch(batch_size).prefetch(1)

train_set = windowed(temp_train, window_size=60, batch_size=120, shuffle_buffer=1000)
test_set = windowed(temp_test, window_size=60, batch_size=120, shuffle_buffer=1000)

model = tf.keras.models.Sequential([
    tf.keras.layers.LSTM(50, return_sequences=True, input_shape=[None, 1]),
    tf.keras.layers.LSTM(50),
    tf.keras.layers.Dense(30, activation="relu"),
    tf.keras.layers.Dense(10, activation="relu"),
    tf.keras.layers.Dense(1),
    ])

tresshold = (train['Temperature'].max() - train['Temperature'].min()) * 10/100
print(tresshold)

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if (logs.get('mae')<tresshold) & (logs.get('val_mae')<tresshold):
      print('\sudah mencapai <10%!')
      self.model.stop_training = True

callbacks = myCallback()

optimizer = tf.keras.optimizers.SGD(learning_rate=1.0000e-04, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

history = model.fit(train_set, 
                    validation_data=(test_set),
                    epochs=100,
                    verbose=2,
                    callbacks=[callbacks])

mae = history.history['mae']
val_mae = history.history['val_mae']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(mae) + 1)

plt.plot(mae)
plt.plot(val_mae)
plt.title('Grafik Akurasi')
plt.xlabel('Epoch')
plt.ylabel('Mae')
plt.legend(['train', 'val'], loc = 'best')

plt.plot(loss)
plt.plot(val_loss)
plt.title('Grafik Akurasi')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(['train', 'val'], loc = 'best')