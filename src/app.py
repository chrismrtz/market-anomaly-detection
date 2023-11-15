import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import yfinance as yf
import sys

from anom import clean_data, engineer_features, detect_anomalies

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='stock-selector',
        options=[
            {'label': 'Apple', 'value': 'AAPL'},
            {'label': 'Google', 'value': 'GOOGL'},
            {'label': 'Microsoft', 'value': 'MSFT'}
        ],
        value='AAPL'  # Default value
    ),
    dcc.Graph(id='price-graph'),
])

@app.callback(
    Output('price-graph', 'figure'),
    [Input('stock-selector', 'value')]
)
def update_graph(selected_ticker):
    df = yf.download(selected_ticker, start="2020-01-01", end="2020-12-31")
    
    # Clean and process data using functions from anom.py
    cleaned_data = clean_data(df)
    featured_data = engineer_features(cleaned_data)
    anomalies = detect_anomalies(featured_data)
    
    # Figure with anomalies marked (can modify the plotting function to accept anomalies data and plot accordingly)
    fig = px.line(df, x=df.index, y='Close', title=f'Stock Prices for {selected_ticker}')
    
    # Anomaly scatter plot over line graph
    fig.add_scatter(x=anomalies.index, y=anomalies['Close'], mode='markers', name='Anomaly')
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
