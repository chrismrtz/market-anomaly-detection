# Currently working on adding a news feature that provides a link to news about the marked anomaly
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import yfinance as yf
import pandas as pd
from datetime import date
import dash_bootstrap_components as dbc

from anomWithNews import clean_data, engineer_features, detect_anomalies, split_data_for_calendar_analysis

import requests
import datetime

def get_news(ticker, anomaly_date):
    api_key = "cb5b6ccedc5d41b3b15072a9ceb9afeb"
    from_date = (anomaly_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    to_date = anomaly_date.strftime("%Y-%m-%d")
    url = (f"https://newsapi.org/v2/everything?q={ticker}&from={from_date}"
           f"&to={to_date}&sortBy=relevancy&apiKey={api_key}")

    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [(article["title"], article["url"]) for article in articles]
    return []


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1('Stock Data Anomaly Detection', style={'textAlign': 'center'}),
    html.Div([
        dcc.Dropdown(
            id='stock-selector',
            options=[{'label': stock, 'value': stock} for stock in ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NYA', 'GME']],
            value='AAPL'
        ),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            display_format='MMM D, YYYY',
            start_date_placeholder_text='Start Date',
            end_date_placeholder_text='End Date'
        )
    ], style={'margin': '20px'}),
    html.Div([
        dcc.RadioItems(
            id='analysis-type',
            options=[
                {'label': 'Standard Analysis', 'value': 'standard'},
                {'label': 'Calendar Effects Analysis', 'value': 'calendar'}
            ],
            value='standard',
            style={'display': 'inline-block', 'marginRight': '10px'}
        ),
        html.Div([
            html.Img(
                src='/assets/info_icon.png',
                id='info-icon',
                style={'height': '20px', 'width': '20px', 'cursor': 'pointer'}
            ),
            dbc.Tooltip(
                children=[
                    html.Span("Calendar Effects Analysis examines stock price movements to identify anomalies that occur during specific calendar periods. "),
                    html.Br(),
                    html.Span("For example, the 'January Effect' refers to the trend where stock prices increase more in January than in other months, historically attributed to increased buying after the sell-off for year-end tax purposes.")
                ],
                target='info-icon',
                placement='right',
                style={'fontSize': '12px'}
            )
        ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
    ]),
    dcc.Dropdown(
        id='effect-type',
        options=[
            {'label': 'January Effect', 'value': 'january'},
            {'label': 'Weekend Effect', 'value': 'weekend'}
            # Add as needed
        ],
        value='january',
        style={'display': 'none'}  # Hidden by default
    ),
    dcc.Graph(id='price-graph'),
], style={'padding': '20px'})

# Callback to update the graph and news section
@app.callback(
    [
        Output('price-graph', 'figure'),
        Output('news-section', 'children')  # Add an output for the news section
    ],
    [Input('stock-selector', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('analysis-type', 'value'),
     Input('effect-type', 'value')]
)
def update_content(selected_ticker, start_date, end_date, analysis_type, effect_type):
    if analysis_type == 'standard':
        anomalies = detect_anomalies(featured_data, selected_ticker)  # Pass ticker
        news_items = []
        for index, anomaly in anomalies.iterrows():
            news = get_news(selected_ticker, anomaly['date'])
            news_items.extend(news)
        # Format the news for display
        news_elements = [html.A(title, href=url, target='_blank') for title, url in news_items]
        return fig, html.Div(news_elements)

@app.callback(
    Output('effect-type', 'style'),
    [Input('analysis-type', 'value')]
)
def toggle_effect_type(analysis_type):
    if analysis_type == 'calendar':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

def update_graph_standard(selected_ticker, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Fetch data using yfinance or existing data pipeline
    df = yf.download(selected_ticker, start=start_date, end=end_date)
    
    # Clean and process data using functions from anom.py
    cleaned_data = clean_data(df)
    featured_data = engineer_features(cleaned_data)
    anomalies = detect_anomalies(featured_data)
    
    fig = px.line(df, x=df.index, y='Close', title=f'Stock Prices for {selected_ticker}')
    
    fig.add_scatter(x=anomalies.index, y=anomalies['Close'], mode='markers', name='Anomalies')

    return fig

def update_graph_for_calendar_analysis(selected_ticker, start_date, end_date, effect_type):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df = yf.download(selected_ticker, start=start_date, end=end_date)

    # Determine the effect period based on the selected effect type
    effect_periods = {
        'january': (1, 1),  # January Effect
        'weekend': (6, 7)   # Weekend Effect (Saturday and Sunday)
    }
    effect_period = effect_periods.get(effect_type, (1, 1))

    train_data, test_data = split_data_for_calendar_analysis(df, start_date, end_date, effect_period)

    # Clean and process both datasets
    cleaned_train_data = clean_data(train_data)
    featured_train_data = engineer_features(cleaned_train_data)
    cleaned_test_data = clean_data(test_data)
    featured_test_data = engineer_features(cleaned_test_data)

    # Detect anomalies in both datasets
    anomalies_train = detect_anomalies(featured_train_data)
    anomalies_test = detect_anomalies(featured_test_data)

    # Create a figure to plot the data
    fig = px.line(df, x=df.index, y='Close', title=f'{effect_type.capitalize()} Effect Analysis for {selected_ticker}')

    # Add scatter plots for anomalies in both datasets
    fig.add_scatter(x=anomalies_train.index, y=anomalies_train['Close'], mode='markers', name='Train Anomalies', marker_color='orange')
    fig.add_scatter(x=anomalies_test.index, y=anomalies_test['Close'], mode='markers', name='Test Anomalies', marker_color='red')

    return fig

app.layout.children.append(html.Div(id='news-section'))


if __name__ == '__main__':
    app.run_server(debug=True)

