# -*- coding: utf-8 -*-
"""21125892005-SundarSingh_Capstone Project

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JdVIGu8gNaHKwlPVACe776Xp65Mjb1AL

# Import the required libraries
"""

import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA,ARMA
#from pmdarima.arima import auto_arima
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
import statsmodels.api as sm

"""1) ! pip install -q kaggle

2) from google.colab import files

files.upload()

3) ! mkdir ~/.kaggle

! cp kaggle.json ~/.kaggle/

4) ! chmod 600 ~/.kaggle/kaggle.json
5) ! kaggle datasets list
! kaggle datasets list
! kaggle competitions download -c 'name-of-competition'
! unzip train.zip -d train
"""

! pip install -q kaggle

#! cp /content/drive/MyDrive/kaggle.json

#cp --help

from google.colab import files
files.upload()

! mkdir ~/.kaggle

! cp kaggle.json ~/.kaggle/

! chmod 600 ~/.kaggle/kaggle.json

! kaggle competitions download jpx-tokyo-stock-exchange-prediction

! unzip jpx-tokyo-stock-exchange-prediction.zip #-d train

"""# To know the what to predict we look the sample submission"""

sample = pd.read_csv("/content/example_test_files/sample_submission.csv")

sample

sample.nunique()

"""#Competition Metrics

JPX Competition Metric
In this competition, the following conditions set will be used to compete for scores.

The model will use the closing price ( 𝐶(𝑘,𝑡) ) until that business day ( 𝑡 ) and other data every business day as input data for a stock ( 𝑘 ), and predict rate of change ( 𝑟(𝑘,𝑡) ) of closing price of the top 200 stocks and bottom 200 stocks on the following business day ( 𝐶(𝑘,𝑡+1) ) to next following business day ( 𝐶(𝑘,𝑡+2) )

𝑟(𝑘,𝑡)=𝐶(𝑘,𝑡+2)−𝐶(𝑘,𝑡+1)𝐶(𝑘,𝑡+1)
 
Within top 200 stock predicted ( 𝑢𝑝𝑖(𝑖=1,2,…,200) ), multiply by their respective rate of change with linear weights of 2-1 for rank 1-200 and denote their sum as  𝑆𝑢𝑝 .

𝑆𝑢𝑝=∑200𝑖=1(𝑟(𝑢𝑝𝑖,𝑡)∗𝑙𝑖𝑛𝑒𝑎𝑟𝑓𝑢𝑛𝑐𝑡𝑖𝑜𝑛(2,1)𝑖))𝐴𝑣𝑒𝑟𝑎𝑔𝑒(𝑙𝑖𝑛𝑒𝑎𝑟𝑓𝑢𝑛𝑐𝑡𝑖𝑜𝑛(2,1))
 
Within bottom 200 stocks predicted ( 𝑑𝑜𝑤𝑛𝑖(𝑖=1,2,…,200) ), multiply by their respective rate of change with linear weights of 2-1 for bottom rank 1-200 and denote their sum as  𝑆𝑑𝑜𝑤𝑛 .

𝑆𝑑𝑜𝑤𝑛=∑200𝑖=1(𝑟(𝑑𝑜𝑤𝑛𝑖,𝑡)∗𝑙𝑖𝑛𝑒𝑎𝑟𝑓𝑢𝑛𝑐𝑡𝑖𝑜𝑛(2,1)𝑖)𝐴𝑣𝑒𝑟𝑎𝑔𝑒(𝑙𝑖𝑛𝑒𝑎𝑟𝑓𝑢𝑛𝑐𝑡𝑖𝑜𝑛(2,1))
 
The result of subtracting  𝑆𝑑𝑜𝑤𝑛  from  𝑆𝑢𝑝  is  𝑅𝑑𝑎𝑦  and is called "daily spread return".

𝑅𝑑𝑎𝑦=𝑆𝑢𝑝−𝑆𝑑𝑜𝑤𝑛
 
The daily spread return is calculated every business day during the public/private period and obtained as a time series for that period. The mean/standard deviation of the time series of daily spread returns is used as the score. Score calculation formula (x is the business day of public/private period)

𝑆𝑐𝑜𝑟𝑒=𝐴𝑣𝑒𝑟𝑎𝑔𝑒(𝑅𝑑𝑎𝑦1−𝑑𝑎𝑦𝑥)𝑆𝑇𝐷(𝑅𝑑𝑎𝑦1−𝑑𝑎𝑦𝑥)
 
The Kagger with the largest score for the private period wins.
"""

stock_prices_train = pd.read_csv("/content/train_files/stock_prices.csv",parse_dates=['Date'],index_col=['Date'])

stock_prices_train

stock_prices_train.info()

stock_prices_train.isnull().sum()

stock_prices_train1 = stock_prices_train.dropna()

stock_prices_train1.isnull().sum()

stock_prices_train1 = stock_prices_train1.drop(columns=['RowId','SupervisionFlag'])

stock_prices_train1.info()

stock_prices_train1.describe()

stock_prices_train['Open'].plot(figsize=(16,7))

stock_prices_train['Close'].plot(figsize=(16,7),c='g',ylabel="Stock Price")

stock_prices_train.plot.line(y=['Open','Close'], figsize=(17,7))

stock_prices_train['Target'].plot(figsize=(16,5))

stock_prices_train.plot.hist(y='Target', figsize=(10,6),bins=200,edgecolor='y')

stock_prices_train['Volume'].plot(figsize=(16,5))

plt.figure(figsize=(17,10))
sns.heatmap(stock_prices_train.corr(), annot=True)

"""# Manual calclations of Target/rate of chage by the help of given metrics

# Let us try to calculate the Target(ie. rate of change) as per given formulae in metrics

# 𝑟(𝑘,𝑡)=(𝐶(𝑘,𝑡+2)−𝐶(𝑘,𝑡+1))/𝐶(𝑘,𝑡+1)

# r = Rate of change
# k = stock
# t = time
"""

# let's take one stock
stock = stock_prices_train[stock_prices_train["SecuritiesCode"]==7777].reset_index(drop=True)
stock.head()

# Applying formulae

stock["rate_of_change"] = (stock["Close"].shift(-2) - stock["Close"].shift(-1)) / stock["Close"].shift(-1)
stock.head()

"""# In above we can observe that given 'Target' and calcuated 'rate of change' are same. Hence our calculation is correct"""

# Now we need to give the rank as per rate of change by descending order
# The rank should be calculated in given stocks 
# let take any date radomly
rank = stock_prices_train[stock_prices_train.index=="2021-12-03"].reset_index(drop=True)
rank.head()

rank["rank"] = rank["Target"].rank(ascending=False,method="first") -1 
rank = rank.sort_values("rank").reset_index(drop=True)

rank

"""# calculating the "Daily spread return" Using Sum up and sum down


# 𝑅𝑑𝑎𝑦 = 𝑆𝑢𝑝−𝑆𝑑𝑜𝑤𝑛

# Within top 200 stock predicted ( 𝑢𝑝𝑖(𝑖=1,2,…,200) ), multiply by their respective rate of change with linear weights of 2-1 for rank 1-200 and denote their sum as  𝑆𝑢𝑝 .

# 𝑆𝑢𝑝 = ∑200𝑖=1(𝑟(𝑢𝑝𝑖,𝑡)∗𝑙𝑖𝑛𝑒𝑎𝑟𝑓𝑢𝑛𝑐𝑡𝑖𝑜𝑛(2,1)𝑖))/𝐴𝑣𝑒𝑟𝑎𝑔𝑒(𝑙𝑖𝑛𝑒𝑎𝑟𝑓𝑢𝑛𝑐𝑡𝑖𝑜𝑛(2,1))

# Within bottom 200 stocks predicted ( 𝑑𝑜𝑤𝑛𝑖(𝑖=1,2,…,200) ), multiply by their respective rate of change with linear weights of 2-1 for bottom rank 1-200 and denote their sum as  𝑆𝑑𝑜𝑤𝑛 .

# 𝑆𝑑𝑜𝑤𝑛=∑200𝑖=1(𝑟(𝑑𝑜𝑤𝑛𝑖,𝑡)∗𝑙𝑖𝑛𝑒𝑎𝑟𝑓𝑢𝑛𝑐𝑡𝑖𝑜𝑛(2,1)𝑖)𝐴𝑣𝑒𝑟𝑎𝑔𝑒(𝑙𝑖𝑛𝑒𝑎𝑟𝑓𝑢𝑛𝑐𝑡𝑖𝑜𝑛(2,1))
 

"""

# Now we need to calculte the "Daily Spread Retun" By using given formulae
#Rday = Sup - Sdown 

# Sup = ∑200𝑖=1(𝑟(𝑢𝑝𝑖,𝑡)∗𝑙𝑖𝑛𝑒𝑎𝑟𝑓𝑢𝑛𝑐𝑡𝑖𝑜𝑛(2,1)𝑖))/𝐴𝑣𝑒𝑟𝑎𝑔𝑒(𝑙𝑖𝑛𝑒𝑎𝑟𝑓𝑢𝑛𝑐𝑡𝑖𝑜𝑛(2,1))

Top_200Stocks = rank.iloc[:200,:]
Top_200Stocks

weights = np.linspace(start=2, stop=1, num=200)
weights

Top_200Stocks["weights"] = weights
Top_200Stocks.head()

Top_200Stocks["calculated_weights"] = Top_200Stocks["Target"] * Top_200Stocks["weights"]
Top_200Stocks.head()

Sup = Top_200Stocks["calculated_weights"].sum()/np.mean(weights)
Sup

Bottom_200Stocks = rank.iloc[-200:,:]
Bottom_200Stocks = Bottom_200Stocks.sort_values("rank",ascending = False).reset_index(drop=True)
Bottom_200Stocks

Bottom_200Stocks["weights"] = weights
Bottom_200Stocks.head()

Bottom_200Stocks["calculated_weights"] = Bottom_200Stocks["Target"] * Bottom_200Stocks["weights"]
Bottom_200Stocks.head()

Sdown = Bottom_200Stocks["calculated_weights"].sum()/np.mean(weights)
Sdown

#daily_spread_return 
Rday = Sup - Sdown
Rday

# Now By appling Time siries  model we can predict lower and upper prices

x = stock_prices_train1[['SecuritiesCode','Close']]
y = stock_prices_train1['Target']
print(x)
print(y)

x.isnull().sum()

y.isnull().sum()

import statsmodels.api as sm
from statsmodels.tsa.stattools import acovf,acf,pacf,pacf_yw,pacf_ols

from pylab import rcParams
rcParams['figure.figsize']=12,3

sm.graphics.tsa.plot_acf(x['Close'],title='Atocorelation: Stocks_Open Price',lags=40)

sm.graphics.tsa.plot_pacf(x['Close'],title='Partial Atocorelation: Stocks_Open Price',lags=40)

from fbprophet import Prophet

def train_ph_model(df):
    m = Prophet()
    ph_df = df[['Close','Date']].copy()
    ph_df.rename(columns={'Close': 'y', 'Date': 'ds'}, inplace=True)
    m.fit(ph_df)
    return m

m = train_ph_model(x["Close"].reset_index().copy())
future_prices = m.make_future_dataframe(periods=56)

forecast = m.predict(future_prices)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(56)

# plot forecast 
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head())
m.plot(forecast);

"""# 2nd model I am appling Nural networks to predict the ranks

# Its a very challenging for me wehen I am appling classroom learn models even in time series method also I faced very challinging. Time series model doing with nural network its very new to me. After observing different models I got below model.Still I am not satisfied with this. Due to time is not sfficent I am uploading up to this. After this I am planning to do xgboost and LSTM methods as well. I need time to do this 
"""

import jpx_tokyo_market_prediction
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

train_data = stock_prices_train1[stock_prices_train1.index < '2021-01-01'].copy()
train_data.shape

valid_data = stock_prices_train1[stock_prices_train1.index >= '2021-01-01'].copy()
valid_data.shape

# percentage of valid data

valid_data.shape[0]/stock_prices_train1.shape[0]*100

"""# selecting needed features"""

train_data = train_data.reset_index(drop=True).drop(columns=['SecuritiesCode','AdjustmentFactor','ExpectedDividend'])
valid_data = valid_data.reset_index(drop=True).drop(columns=['SecuritiesCode','AdjustmentFactor','ExpectedDividend'])

valid_data.head()

train_data.head()

# Define encoding function for numerical features
def encoded_features(feature, name, dataset):
    # Create a Normalization layer for our feature
    normalizer = layers.Normalization()

    # Prepare a Dataset that only yields our feature
    feature_ds = dataset.map(lambda x, y: x[name])
    feature_ds = feature_ds.map(lambda x: tf.expand_dims(x, -1))

    # Learn the statistics of the data
    normalizer.adapt(feature_ds)

    # Normalize the input feature
    encoded_feature = normalizer(feature)
    return encoded_feature

# Applying tensorflow to convert dataframe to dataset
def dataframe_to_dataset_convertion(dataframe):
    dataframe = dataframe.copy()
    labels = dataframe.pop("Target")
    DataSet = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
    DataSet = DataSet.shuffle(buffer_size=len(dataframe))
    return DataSet

train_dataset = dataframe_to_dataset_convertion(train_data)
valid_dataset = dataframe_to_dataset_convertion(valid_data)

for x, y in train_dataset.take(1):
  x,y

x

y

# Batch the dataset
train_dataset = train_dataset.batch(1280)
valid_dataset = valid_dataset.batch(1280)

# Raw numerical features
Open = keras.Input(shape=(1,), name="Open")
High = keras.Input(shape=(1,), name="High")
Low = keras.Input(shape=(1,), name="Low")
Close = keras.Input(shape=(1,), name="Close")
Volume = keras.Input(shape=(1,), name="Volume")

all_inputs = [Open, High, Low, Close, Volume]

# Encode numerical features
open_encoded = encoded_features(Open, "Open", train_dataset)
high_encoded = encoded_features(High, "High", train_dataset)
low_encoded = encoded_features(Low, "Low", train_dataset)
close_encoded = encoded_features(Close, "Close", train_dataset)
volume_encoded = encoded_features(Volume, "Volume", train_dataset)

import keras
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed, BatchNormalization, MaxPooling1D, AveragePooling1D

# Concat all features of input layer
attributes = layers.concatenate(
    [
        open_encoded,
        high_encoded,
        low_encoded,
        close_encoded,
        volume_encoded,
    ]
)

# Adding hidden layers, batch_normalization layers and dropout layers
x = layers.Dense(128, activation="relu")(attributes)
x = layers.BatchNormalization()(x)
x = layers.Dropout(0.2)(x)
x = layers.Dense(128, activation="relu")(x)
x = layers.BatchNormalization()(x)
x = layers.Dropout(0.2)(x)
x = layers.Dense(64, activation="relu")(x)
x = layers.BatchNormalization()(x)
x = layers.Dropout(0.2)(x)

# Output layer for regression task
output = layers.Dense(1, activation="linear")(x)

# Create our NN model
model = keras.Model(all_inputs, output)
model.compile("adam", "mse", metrics=[tf.keras.metrics.RootMeanSquaredError()])

model.summary()

early_stopping = keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=10,
    min_delta=1e-3,
    restore_best_weights=True,
)

model.fit(train_dataset, epochs=200, validation_data=valid_dataset, callbacks=[early_stopping])

model.save("sndar")

# Load trained model
best_model = keras.models.load_model("sndar")

# Generate tensorflow dataset for test data
def dataframe_to_dataset_test(dataframe):
    dataframe = dataframe.copy()
    ds = tf.data.Dataset.from_tensor_slices(dict(dataframe))
    return ds

# Make predictions
env = jpx_tokyo_market_prediction.make_env()   # initialize the environment
iter_test = env.iter_test()    # an iterator which loops over the test files
for (prices, options, financials, trades, secondary_prices, sample_prediction) in iter_test:
    test_ds = dataframe_to_dataset_test(prices)
    sample_prediction['target_pred'] = best_model.predict(test_ds)
    sample_prediction = sample_prediction.sort_values(by="target_pred", ascending=False)
    sample_prediction['Rank'] = np.arange(2000)
    sample_prediction = sample_prediction.sort_values(by="SecuritiesCode", ascending=True)
    sample_prediction.drop(['target_pred'], axis=1, inplace=True)
    display(sample_prediction)
    env.predict(sample_prediction)   # register your predictions

