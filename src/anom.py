import yfinance as yf
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, f1_score
import matplotlib.pyplot as plt

from sklearn.impute import SimpleImputer

def clean_data(data):
    # Fill forward for missing values
    data.ffill(inplace=True)
    
    # Impute any remaining missing values after fill forward
    imputer = SimpleImputer(strategy='mean')  # or use another strategy
    data_imputed = imputer.fit_transform(data)
    data = pd.DataFrame(data_imputed, columns=data.columns, index=data.index)
    
    # Drop rows that still have NaN values (if any)
    data.dropna(inplace=True)
    return data

'''
def clean_data(data):
    data.ffill(inplace=True)
    data.dropna(inplace=True)
    return data'''

def engineer_features(data):
    data['MA_5'] = data['Close'].rolling(window=5).mean()
    data['MA_10'] = data['Close'].rolling(window=10).mean()
    data['Pct_change'] = data['Close'].pct_change()
    
    # Fill NaN values created by rolling functions
    data['MA_5'].fillna(value=data['Close'].mean(), inplace=True)
    data['MA_10'].fillna(value=data['Close'].mean(), inplace=True)
    data['Pct_change'].fillna(value=data['Pct_change'].mean(), inplace=True)

    scaler = StandardScaler()
    data['Volume_scaled'] = scaler.fit_transform(data[['Volume']])
    
    return data


def detect_anomalies(data):
    # Check for NaN values and print columns with NaN
    if data.isnull().any().any():
        print("NaN values found in the following columns before model fitting:")
        print(data.columns[data.isnull().any()])
        raise ValueError("NaN values found in data before model fitting.")

    model = IsolationForest(n_estimators=100, contamination=0.01)
    model.fit(data)
    data['anomaly'] = model.predict(data)
    anomalies = data[data['anomaly'] == -1]
    return anomalies


def evaluate_model(true_labels, predicted_labels):
    print(classification_report(true_labels, predicted_labels))
    f1 = f1_score(true_labels, predicted_labels, pos_label=-1)
    print(f'F1 Score: {f1}')
    return f1

def plot_data_with_anomalies(data, ticker):
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Close'], label='Close Price', color='blue')
    anomalies = data[data['anomaly'] == -1]
    plt.scatter(anomalies.index, anomalies['Close'], color='red', label='Anomaly')
    plt.title(f'Stock Price and Anomalies for {ticker}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

def tune_model(data):
    best_f1 = 0
    best_model = None
    features = data.drop(['anomaly'], axis=1, errors='ignore')  # Drop 'anomaly' column if it exists

    for n_estimators in [50, 100, 200]:
        for contamination in [0.01, 0.02, 0.05]:
            model = IsolationForest(n_estimators=n_estimators, contamination=contamination)
            model.fit(features)
            predicted_labels = model.predict(features)
            # Create a temporary 'anomaly' column for F1 score calculation
            data['temp_anomaly'] = predicted_labels
            f1 = f1_score(data['temp_anomaly'], predicted_labels, pos_label=-1)
            if f1 > best_f1:
                best_f1 = f1
                best_model = model

    # Clean up: remove the temporary column
    data.drop(['temp_anomaly'], axis=1, inplace=True)
    return best_model, best_f1

def main():
    ticker_list = ['AAPL', 'GOOG', 'MSFT']
    start_date = '2020-01-01'
    end_date = '2020-12-31'

    for ticker in ticker_list:
        data = yf.download(ticker, start=start_date, end=end_date)
        cleaned_data = clean_data(data)
        featured_data = engineer_features(cleaned_data)

        # Check for NaN values after feature engineering
        if featured_data.isnull().values.any():
            print(f"NaN values found in featured data for {ticker}")
            featured_data = clean_data(featured_data)
    
        best_model, best_f1 = tune_model(featured_data)
        print(f'Best model for {ticker} with F1 score: {best_f1}')


        anomalies = detect_anomalies(featured_data)

        # compare the detected anomalies with the true labels
        # placeholder since we don't have true labels
        # true_labels = get_true_labels_somehow()
        # predicted_labels = anomalies['anomaly']
        # evaluate_model(true_labels, predicted_labels)

        print(f'Anomalies for {ticker}:\n{anomalies}\n')

        plot_data_with_anomalies(featured_data, ticker)

if __name__ == '__main__':
    main()

