# Market Anomaly Detection Project

## Overview
This project provides an innovative tool for detecting anomalies in the stock market, leveraging historical data primarily from Yahoo Finance. It focuses on real-time anomaly detection, highlighting unusual patterns and trends that might indicate significant market events.

## Structure
- `src/`: Contains the core source code, including scripts for data processing and anomaly detection.
- `dashboard/`: Houses the interactive web dashboard built with Dash for a dynamic user interface.
- `anom.py`: The main script for data fetching, preprocessing, and anomaly detection using the Isolation Forest algorithm.
- `app.py`: The Dash application script for running the interactive dashboard.

## Setup and Installation
1. Clone the repository: `git clone https://github.com/yourusername/market-anomaly-detection.git`
2. Navigate to the project folder: `cd market-anomaly-detection`
3. Install dependencies: `pip install -r requirements.txt`

## Usage
### Anomaly Detection Script
- Navigate to `src/`.
- Execute: `python3 anom.py` to run the anomaly detection analysis.

### Interactive Dashboard
- Run: `python app.py` from the `src/` directory.
- Access the dashboard at `http://127.0.0.1:8050/` in your web browser.

### Dashboard Features
- Select different stocks and time frames for analysis.
- Choose between standard analysis and calendar effects analysis (e.g., January Effect, Weekend Effect).
- Visualize stock data with highlighted anomalies.

## Progress and Enhancements
- Implemented a comprehensive anomaly detection system using machine learning.
- Developed an interactive dashboard for user engagement and better data visualization.
- Integrated calendar effects analysis, adding a unique perspective to anomaly detection.
- Future plans include expanding the dataset, incorporating more sophisticated machine learning models, and further refining the user experience.

