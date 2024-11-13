import dash
from dash import dcc, html
import dash.dependencies as dd
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import random
import os
from heart_rate_engine import calculate_heart_rate  # Import the heart rate calculation engine
# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Change the current working directory to the script's directory
os.chdir(script_dir)


# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Vital Signs Monitoring System"

# Read ECG and PPG data from CSV files (assumes no headers, single column)
ecg_df = pd.read_csv('../data/ECG.csv', header=None, names=['ECG'])  # ECG signal data
ppg_df = pd.read_csv('../data/PPG.csv', header=None, names=['PPG'])  # PPG signal data
temp_df = pd.read_csv('../data/TEMP.csv', header=None, names=['Temp'])  # Temperature data

# Generate a time series in milliseconds (1 ms per step)
sampling_rate = 1000  # 1000 Hz = 1 ms per sample
time_series = np.arange(0, len(ecg_df) * (1 / sampling_rate), 1 / sampling_rate)  # Time in seconds

# Define a sliding window size (e.g., showing 1 second of data at a time)
window_size = 1000  # Show the latest 1000 data points (1 second at 1000 Hz)

# Define the app layout with heart rate, SpO2, respiratory rate, and body temperature
app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    
    # Interval for updating plots (real-time updates every 50 ms)
    dcc.Interval(
        id='interval-component-graphs',
        interval=50,  # Update plots every 50 milliseconds for real-time behavior
        n_intervals=0
    ),
    
    # Interval for updating vital signs (heart rate, etc.)
    dcc.Interval(
        id='interval-component-vitals',
        interval=1000,  # Update vital signs every second
        n_intervals=0
    ),

    # Grid layout with ECG, PPG plots and vital signs
    html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(5, 1fr)', 'gap': '10px'}, children=[
        # ECG plot spanning two rows
        html.Div(style={'gridColumn': 'span 4', 'gridRow': 'span 2', 'border': '1px solid white', 'padding': '10px'}, children=[
            dcc.Graph(id='ecg-plot', config={'displayModeBar': False}),
        ]),
        
        # Heart Rate in the first row, last column
        html.Div(style={'border': '1px solid white', 'padding': '10px'}, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("♥", style={'color': 'red', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='heart-rate-value', style={'fontSize': '60px', 'color': 'red', 'fontWeight': 'bold'})
            ])
        ]),
        
        # Respiratory Rate
        html.Div(style={'border': '1px solid white', 'padding': '10px'}, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🌬️", style={'color': 'yellow', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='respiratory-rate-value', style={'fontSize': '60px', 'color': 'yellow', 'fontWeight': 'bold'})
            ])
        ]),

        # PPG plot spanning two rows
        html.Div(style={'gridColumn': 'span 4', 'gridRow': 'span 2', 'border': '1px solid white', 'padding': '10px'}, children=[
            dcc.Graph(id='ppg-plot', config={'displayModeBar': False}),
        ]),
        
        # SpO2 Value in the second row, last column
        html.Div(style={'border': '1px solid white', 'padding': '10px'}, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🫁", style={'color': 'lightblue', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='spo2-value', style={'fontSize': '60px', 'color': 'lightblue', 'fontWeight': 'bold'})
            ])
        ]),
        
        # Body Temperature
        html.Div(style={'border': '1px solid white', 'padding': '10px'}, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🌡️", style={'color': 'orange', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='body-temp-value', style={'fontSize': '60px', 'color': 'orange', 'fontWeight': 'bold'})
            ])
        ]),
    ]),
])

# Global variables for keeping track of current data index
current_index = 0

# Callback to update the ECG and PPG plots in real-time
@app.callback(
    [dd.Output('ecg-plot', 'figure'),
     dd.Output('ppg-plot', 'figure')],
    [dd.Input('interval-component-graphs', 'n_intervals')]
)
def update_graphs(n):
    global current_index, ecg_df, ppg_df, time_series, window_size

    # Select the next chunk of data to simulate real-time streaming
    start_index = current_index
    end_index = current_index + window_size

    # Ensure that the end_index does not exceed the length of the dataframes
    if end_index > len(ecg_df):
        end_index = len(ecg_df)
        start_index = end_index - window_size  # Adjust start_index accordingly
        if start_index < 0:
            start_index = 0  # Prevent negative indexing

    # Update the current index for the next interval
    current_index = (current_index + 10) % len(ecg_df)

    # Slice the data to get the current window of data
    ecg_window = ecg_df['ECG'].iloc[start_index:end_index]
    ppg_window = ppg_df['PPG'].iloc[start_index:end_index]
    time_window = time_series[start_index:end_index]

    # Create ECG plot
    ecg_fig = go.Figure()
    ecg_fig.add_trace(go.Scatter(x=time_window, y=ecg_window, mode='lines', name='ECG', line=dict(color='red', width=5)))
    ecg_fig.update_layout(
        title='ECG',
        title_font=dict(size=50),
        xaxis_title='Time (s)',
        yaxis_title='Amplitude',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )
    
    # Create PPG plot
    ppg_fig = go.Figure()
    ppg_fig.add_trace(go.Scatter(x=time_window, y=ppg_window, mode='lines', name='PPG', line=dict(color='lightblue', width=5)))
    ppg_fig.update_layout(
        title='PPG',
        title_font=dict(size=50),
        xaxis_title='Time (s)',
        yaxis_title='Amplitude',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )

    return ecg_fig, ppg_fig

# Callback to update the vital signs
@app.callback(
    [dd.Output('heart-rate-value', 'children'),
     dd.Output('spo2-value', 'children'),
     dd.Output('respiratory-rate-value', 'children'),
     dd.Output('body-temp-value', 'children')],
    [dd.Input('interval-component-vitals', 'n_intervals')]
)
def update_vital_signs(n):
    global current_index, ecg_df, ppg_df, temp_df

    # Get the current window of ECG data
    start_index = current_index
    end_index = current_index + window_size
    ecg_window = ecg_df['ECG'].iloc[start_index:end_index]
    
    # Calculate heart rate from ECG data
    heart_rate = calculate_heart_rate(ecg_window)  # Calculate heart rate from ECG
    
    # Get random values for other vital signs
    spo2 = random.randint(92, 100)
    respiratory_rate = random.randint(12, 20)
    body_temp = temp_df['Temp'].iloc[start_index % len(temp_df)]  # Fetch temperature data
    
    # Update the heart rate and other values
    return f"{heart_rate:.1f} bpm", f"{spo2} %", f"{respiratory_rate} /min", f"{body_temp:.1f} °C"

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
