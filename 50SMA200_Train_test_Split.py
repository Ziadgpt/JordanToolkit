import yfinance as yf
import matplotlib.pyplot as plt

data = yf.download('gc=f', start='2023-01-01')
data = data[['Close']]


data['SMA50'] = data['Close'].rolling(50).mean()
data['SMA200'] = data['Close'].rolling(200).mean()
data['Return'] = data['Close'].pct_change()
data['Direction'] = (data['Return'].shift(-1) > 0).astype(int)
data.dropna(inplace=True)


from sklearn.model_selection import train_test_split

features = ['SMA50', 'SMA200', 'Return']
X = data[features]
y = data['Direction']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))

X_test['Prediction'] = y_pred
X_test['SMA50'] = data.loc[X_test.index, 'SMA50']
X_test['SMA200'] = data.loc[X_test.index, 'SMA200']
X_test['Close'] = data.loc[X_test.index, 'Close']

X_test['Signal'] = ((X_test['Prediction'] == 1) & (X_test['SMA50'] > X_test['SMA200'])).astype(int)
X_test['Strategy'] = X_test['Signal'].shift(1) * X_test['Close'].pct_change()

# Cumulative return
(1 + X_test['Strategy']).cumprod().plot(title='ML + SMA Strategy vs. Buy & Hold')
