"""====================================================================================
                        ------->  Revision History  <------
====================================================================================

Date            Who         Ver         Changes
====================================================================================
11-Nov-24       SM          1000        Initial creation
===================================================================================="""

import dash
from dash import dcc, html
import dash.dependencies as dd
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os
from filter_engine import low_pass_filter  # Import the filtering engine for ECG and PPG data
from heart_rate_engine import calculate_heart_rate  # Import the function for calculating heart rate from ECG data
from alarm_engine import check_vital_signs  # Import the function to check the status of vital signs (alarm check)
from config import SAMPLING_RATE, WINDOW_SIZE, DATA_DIR, COLORS, HEART_RATE_PARAMS  # Import configuration parameters like sampling rate and file paths

# Helper function to create a Plotly figure
def create_figure(time_window, data, title, line_color):
    """
    Creates a Plotly figure for plotting the data.

    Args:
        time_window (array): The time data for the x-axis (time series).
        data (array): The data to be plotted (e.g., ECG or PPG).
        title (str): The title for the graph (e.g., "ECG" or "PPG").
        line_color (str): The color of the line in the graph.

    Returns:
        go.Figure: A Plotly figure object with the plotted data.
    """
    min_val, max_val = data.min(), data.max()  # Calculate the min and max of the data to set the y-axis range
    margin = 0.35 * (max_val - min_val)  # Add some margin to the y-axis
    fig = go.Figure()  # Initialize a Plotly figure
    fig.add_trace(go.Scatter(x=time_window, y=data, mode='lines', name=title, line=dict(color=line_color, width=5)))
    # Update layout with titles, background color, font color, and y-axis range
    fig.update_layout(
        title=title,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        yaxis=dict(range=[min_val - margin, max_val + margin])  # Set the y-axis range with some margin
    )
    return fig

# Get the directory of the current script to ensure relative file paths are correct
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)  # Change the working directory to the script's directory

# Initialize Dash app for the web-based interface
app = dash.Dash(__name__)
app.title = "Vital Signs Monitoring System"  # Set the title of the web page

# Load data files (ECG, PPG, TEMP) from the specified directory
ecg_df = pd.read_csv(os.path.join(DATA_DIR, 'ECG.csv'), header=None, names=['ECG'])
ppg_df = pd.read_csv(os.path.join(DATA_DIR, 'PPG.csv'), header=None, names=['PPG'])
temp_df = pd.read_csv(os.path.join(DATA_DIR, 'TEMP.csv'), header=None, names=['Temp'])

# Generate a time series (1 ms per step) based on the sampling rate and the length of the data
time_series = np.arange(0, len(ecg_df) * (1 / SAMPLING_RATE), 1 / SAMPLING_RATE)

# Define styling for common elements and grid layout
common_style = {'border': '1px solid white', 'padding': '10px'}
grid_layout_style = {'display': 'grid', 'gridTemplateColumns': 'repeat(5, 1fr)', 'gap': '10px'}

# Define the layout of the web page using Dash HTML components
app.layout = html.Div(style={'backgroundColor': COLORS['background'], 'color': COLORS['text'], 'padding': '20px'}, children=[
    dcc.Store(id='current-index-store', data=0),  # Store component to keep track of the current data index
    dcc.Interval(id='interval-component-graphs', interval=50, n_intervals=0),  # Interval component for graph updates (50ms)
    dcc.Interval(id='interval-component-vitals', interval=1000, n_intervals=0),  # Interval component for vital signs updates (1 second)
    
    # Grid layout with components for ECG graph, vital sign containers, and PPG graph
    html.Div(style=grid_layout_style, children=[
        html.Div(style={'gridColumn': 'span 4', 'gridRow': 'span 2', **common_style},
                 children=[dcc.Graph(id='ecg-plot', config={'displayModeBar': False})]),  # ECG plot
        html.Div(id='heart-rate-container', style=common_style, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("♥", style={'color': 'red', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='heart-rate-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})  # Heart rate value
            ])
        ]),
        html.Div(id='respiratory-rate-container', style=common_style, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🌬️", style={'color': 'white', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='respiratory-rate-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})  # Respiratory rate value
            ])
        ]),
        html.Div(style={'gridColumn': 'span 4', 'gridRow': 'span 2', **common_style},
                 children=[dcc.Graph(id='ppg-plot', config={'displayModeBar': False})]),  # PPG plot
        html.Div(id='spo2-container', style=common_style, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🫁", style={'color': 'white', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='spo2-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})  # SpO2 value
            ])
        ]),
        html.Div(id='body-temp-container', style=common_style, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🌡️", style={'color': 'white', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='body-temp-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})  # Body temp value
            ])
        ]),
    ]),
])

# Global index to keep track of the current position in the streaming data
current_index = 0

# Callback to update the ECG and PPG plots based on the current index
@app.callback(
    [dd.Output('ecg-plot', 'figure'),
     dd.Output('ppg-plot', 'figure'),
     dd.Output('current-index-store', 'data')],  # Update the store with the new index
    [dd.Input('interval-component-graphs', 'n_intervals')],
    [dd.State('current-index-store', 'data')]  # Get the current index from the store
)
def update_graphs(n, current_index):
    # Define the start and end index based on the current index and window size
    start_index = current_index
    end_index = current_index + WINDOW_SIZE
    if end_index > len(ecg_df):
        end_index = len(ecg_df)
        start_index = end_index - WINDOW_SIZE
        if start_index < 0:
            start_index = 0

    # Update the current index for the next cycle
    new_index = (current_index + 10) % len(ecg_df)

    # Extract windows of ECG and PPG data for the current time range
    ecg_window = ecg_df['ECG'].iloc[start_index:end_index].to_numpy()
    ppg_window = ppg_df['PPG'].iloc[start_index:end_index].to_numpy()
    time_window = time_series[start_index:end_index]

    # Apply low-pass filtering to ECG and PPG data
    ecg_filtered = low_pass_filter(ecg_window, cutoff_freq=40, sampling_rate=SAMPLING_RATE, padding=True)
    ppg_filtered = low_pass_filter(ppg_window, cutoff_freq=5, sampling_rate=SAMPLING_RATE, padding=True)

    # Create Plotly figures for ECG and PPG
    ecg_fig = create_figure(time_window, ecg_filtered, 'ECG', 'red')
    ppg_fig = create_figure(time_window, ppg_filtered, 'PPG', 'lightblue')

    return ecg_fig, ppg_fig, new_index  # Return the new index to update the store

# Callback to update the vital sign values and their corresponding alarm colors
@app.callback(
    [dd.Output('heart-rate-value', 'children'),
     dd.Output('spo2-value', 'children'),
     dd.Output('respiratory-rate-value', 'children'),
     dd.Output('body-temp-value', 'children'),
     dd.Output('heart-rate-container', 'style'),
     dd.Output('spo2-container', 'style'),
     dd.Output('respiratory-rate-container', 'style'),
     dd.Output('body-temp-container', 'style')],
    [dd.Input('interval-component-vitals', 'n_intervals')],
    [dd.State('current-index-store', 'data')]  # Fetch current index from the store
)
def update_vital_signs(n, current_index):
    # Define the start and end index for vital sign data
    start_index = current_index
    end_index = current_index + WINDOW_SIZE
    ecg_window = ecg_df['ECG'].iloc[start_index:end_index]
    
    # Get the parameters from the config file
    sampling_rate = HEART_RATE_PARAMS['sampling_rate']
    peak_height_factor = HEART_RATE_PARAMS['peak_height_factor']
    min_peak_distance = HEART_RATE_PARAMS['min_peak_distance']

    # Calculate heart rate using the parameterized function
    heart_rate = calculate_heart_rate(ecg_window, sampling_rate=sampling_rate, 
                                      peak_height_factor=peak_height_factor, 
                                      min_peak_distance=min_peak_distance)
    
    # Simulate other vital signs (SpO2, respiratory rate, body temp)
    spo2 = np.random.randint(92, 100)
    respiratory_rate = np.random.randint(12, 20)
    body_temp = temp_df['Temp'].iloc[start_index % len(temp_df)]

    # Check vital signs and set alarm colors
    heart_rate_color, spo2_color, respiratory_rate_color, body_temp_color = check_vital_signs(
        heart_rate, spo2, respiratory_rate, body_temp)

    # Return the updated vital sign values along with their alarm colors
    return (
        f"{heart_rate:.1f} bpm", f"{spo2} %", f"{respiratory_rate} /min", f"{body_temp:.1f} °C",
        {'backgroundColor': heart_rate_color, 'color': 'white', 'fontWeight': 'bold'},
        {'backgroundColor': spo2_color, 'color': 'white', 'fontWeight': 'bold'},
        {'backgroundColor': respiratory_rate_color, 'color': 'white', 'fontWeight': 'bold'},
        {'backgroundColor': body_temp_color, 'color': 'white', 'fontWeight': 'bold'}
    )

# Run the app on the local server
if __name__ == '__main__':
    app.run_server(debug=True)
