import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import yfinance as yf
import pandas as pd
from datetime import date
import dash_bootstrap_components as dbc

from anom import clean_data, engineer_features, detect_anomalies, split_data_for_calendar_analysis

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Stock Data Anomaly Detection'),
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
    ),
    dcc.RadioItems(
        id='analysis-type',
        options=[
            {'label': 'Standard Analysis', 'value': 'standard'},
            {'label': 'Calendar Effects Analysis', 'value': 'calendar'}
        ],
        value='standard'
    ),
    html.Div([
        html.Img(
            src='/assets/info_icon.png',
            id='info-icon',
            style={
                'height': '10px',
                'width': '10px',
                'margin-left': '5px',
                'cursor': 'pointer'
            }
        ),
        dbc.Tooltip(
            children=[
                html.Span("Calendar Effects Analysis examines stock price movements to identify anomalies that occur during specific calendar periods. "),
                html.Br(),
                html.Span("For example, the 'January Effect' refers to the trend where stock prices increase more in January than in other months, historically attributed to increased buying after the sell-off for year-end tax purposes.")
            ],
            target='info-icon',
            placement='right',
            style={'fontSize': '12px', 'margin-left': '5px', 'paddint-top' : '10px'}
        )
    ], style={'display': 'inline-block', 'marginLeft': '5px', 'padding-top': '10px'}),
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
])

@app.callback(
    Output('effect-type', 'style'),
    [Input('analysis-type', 'value')]
)
def toggle_effect_type(analysis_type):
    if analysis_type == 'calendar':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('price-graph', 'figure'),
    [Input('stock-selector', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('analysis-type', 'value'),
     Input('effect-type', 'value')]
)
def update_graph(selected_ticker, start_date, end_date, analysis_type, effect_type):
    if analysis_type == 'standard':
        return update_graph_standard(selected_ticker, start_date, end_date)
    elif analysis_type == 'calendar':
        return update_graph_for_calendar_analysis(selected_ticker, start_date, end_date, effect_type)

def update_graph_standard(selected_ticker, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
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
        # Add as needed
    }
    effect_period = effect_periods.get(effect_type, (1, 1))

    # Split data for calendar analysis
    train_data, test_data = split_data_for_calendar_analysis(df, start_date, end_date, effect_period)

    # Clean & process both datasets
    cleaned_train_data = clean_data(train_data)
    featured_train_data = engineer_features(cleaned_train_data)
    cleaned_test_data = clean_data(test_data)
    featured_test_data = engineer_features(cleaned_test_data)

    # Detect anomalies in both datasets
    anomalies_train = detect_anomalies(featured_train_data)
    anomalies_test = detect_anomalies(featured_test_data)

    # Create figure to plot data
    fig = px.line(df, x=df.index, y='Close', title=f'{effect_type.capitalize()} Effect Analysis for {selected_ticker}')

    # Add scatter plots for anomalies in both datasets
    fig.add_scatter(x=anomalies_train.index, y=anomalies_train['Close'], mode='markers', name='Train Anomalies', marker_color='orange')
    fig.add_scatter(x=anomalies_test.index, y=anomalies_test['Close'], mode='markers', name='Test Anomalies', marker_color='red')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

