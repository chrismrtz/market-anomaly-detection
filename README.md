# Market Anomaly Detection

## Project Overview
This project aims to detect anomalies in financial markets in real-time or near real-time. By focusing on a specific asset class, the system will monitor for unusual activities that could indicate significant market events. The motivation for this project is to prevent incidents like the 2012 Knight Capital glitch, which led to substantial financial loss.

## Data Sources
The data for this project is sourced from the following financial APIs, including:
- Yahoo Finance (using `yfinance` library)

## Features
The system will monitor the following features for anomaly detection:
- Moving Averages
- Trading Volumes
- Price Fluctuations

## Methodology
A combination of machine learning algorithms and statistical methods will be used to detect anomalies. A sliding window approach will simulate real-time data analysis.

## Metrics
The performance of the anomaly detection system will be evaluated using:
- Accuracy
- Precision
- F1 Score

## Installation
To set up the project environment, run the following command to install the required packages:
```bash
pip install -r requirements.txt

