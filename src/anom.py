# Import necessary libraries
import yfinance as yf
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, f1_score

# Function to clean data
def clean_data(data):
    data.ffill(inplace=True)
    data.dropna(inplace=True)
    return data

# Function to engineer features
def engineer_features(data):
    data['MA_5'] = data['Close'].rolling(window=5).mean()
    data['MA_10'] = data['Close'].rolling(window=10).mean()
    data['Pct_change'] = data['Close'].pct_change()
    scaler = StandardScaler()
    data['Volume_scaled'] = scaler.fit_transform(data[['Volume']])
    return data

# Anomaly Detection using Isolation Forest
def detect_anomalies(data):
    model = IsolationForest(n_estimators=100, contamination=0.01)
    model.fit(data)
    data['anomaly'] = model.predict(data)
    anomalies = data[data['anomaly'] == -1]
    return anomalies

# Function to evaluate the model
def evaluate_model(true_labels, predicted_labels):
    print(classification_report(true_labels, predicted_labels))
    f1 = f1_score(true_labels, predicted_labels, pos_label=-1)
    print(f'F1 Score: {f1}')
    return f1

# Define the main function
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
            featured_data.dropna(inplace=True)

        anomalies = detect_anomalies(featured_data)

        # Here you would compare the detected anomalies with the true labels
        # This is just a placeholder since we don't have true labels
        # true_labels = get_true_labels_somehow()
        # predicted_labels = anomalies['anomaly']
        # evaluate_model(true_labels, predicted_labels)

        print(f'Anomalies for {ticker}:\n{anomalies}\n')

if __name__ == '__main__':
    main()

