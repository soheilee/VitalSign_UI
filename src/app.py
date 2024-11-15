import dash
from dash import dcc, html
import dash.dependencies as dd
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os
from filter_engine import low_pass_filter  # Import the filtering engine
from heart_rate_engine import calculate_heart_rate  # For heart rate calculation
from alarm_engine import check_vital_signs  # For alarm checks
from config import SAMPLING_RATE, WINDOW_SIZE, DATA_DIR, COLORS

# Helper function to create a plotly figure
def create_figure(time_window, data, title, line_color):
    """
    Creates a plotly figure with a given data and title.
    
    Args:
        time_window (array): The time data for the x-axis.
        data (array): The data to be plotted.
        title (str): The title for the graph.
        line_color (str): The color of the line.

    Returns:
        go.Figure: A plotly figure object.
    """
    min_val, max_val = data.min(), data.max()
    margin = 0.35 * (max_val - min_val)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_window, y=data, mode='lines', name=title, line=dict(color=line_color, width=5)))
    fig.update_layout(
        title=title,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        yaxis=dict(range=[min_val - margin, max_val + margin])
    )
    return fig

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Vital Signs Monitoring System"

# Load data using os.path.join to handle file paths safely
ecg_df = pd.read_csv(os.path.join(DATA_DIR, 'ECG.csv'), header=None, names=['ECG'])
ppg_df = pd.read_csv(os.path.join(DATA_DIR, 'PPG.csv'), header=None, names=['PPG'])
temp_df = pd.read_csv(os.path.join(DATA_DIR, 'TEMP.csv'), header=None, names=['Temp'])

# Generate time series (1 ms per step)
time_series = np.arange(0, len(ecg_df) * (1 / SAMPLING_RATE), 1 / SAMPLING_RATE)

# Layout styling
common_style = {'border': '1px solid white', 'padding': '10px'}
grid_layout_style = {'display': 'grid', 'gridTemplateColumns': 'repeat(5, 1fr)', 'gap': '10px'}

# Define layout
app.layout = html.Div(style={'backgroundColor': COLORS['background'], 'color': COLORS['text'], 'padding': '20px'}, children=[
    dcc.Store(id='current-index-store', data=0),  # Store for current_index
    dcc.Interval(id='interval-component-graphs', interval=50, n_intervals=0),
    dcc.Interval(id='interval-component-vitals', interval=1000, n_intervals=0),
    html.Div(style=grid_layout_style, children=[
        html.Div(style={'gridColumn': 'span 4', 'gridRow': 'span 2', **common_style},
                 children=[dcc.Graph(id='ecg-plot', config={'displayModeBar': False})]),
        html.Div(id='heart-rate-container', style=common_style, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("♥", style={'color': 'red', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='heart-rate-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
            ])
        ]),
        html.Div(id='respiratory-rate-container', style=common_style, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🌬️", style={'color': 'white', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='respiratory-rate-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
            ])
        ]),
        html.Div(style={'gridColumn': 'span 4', 'gridRow': 'span 2', **common_style},
                 children=[dcc.Graph(id='ppg-plot', config={'displayModeBar': False})]),
        html.Div(id='spo2-container', style=common_style, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🫁", style={'color': 'white', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='spo2-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
            ])
        ]),
        html.Div(id='body-temp-container', style=common_style, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🌡️", style={'color': 'white', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='body-temp-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
            ])
        ]),
    ]),
])

# Global index to keep track of streaming data
current_index = 0

@app.callback(
    [dd.Output('ecg-plot', 'figure'),
     dd.Output('ppg-plot', 'figure'),
     dd.Output('current-index-store', 'data')],  # Update the store with the new index
    [dd.Input('interval-component-graphs', 'n_intervals')],
    [dd.State('current-index-store', 'data')]  # State input to get the current index from the store
)
def update_graphs(n, current_index):
    start_index = current_index
    end_index = current_index + WINDOW_SIZE
    if end_index > len(ecg_df):
        end_index = len(ecg_df)
        start_index = end_index - WINDOW_SIZE
        if start_index < 0:
            start_index = 0

    # Update current_index for the next cycle
    new_index = (current_index + 10) % len(ecg_df)

    ecg_window = ecg_df['ECG'].iloc[start_index:end_index].to_numpy()
    ppg_window = ppg_df['PPG'].iloc[start_index:end_index].to_numpy()
    time_window = time_series[start_index:end_index]

    ecg_filtered = low_pass_filter(ecg_window, cutoff_freq=40, sampling_rate=SAMPLING_RATE, padding=True)
    ppg_filtered = low_pass_filter(ppg_window, cutoff_freq=5, sampling_rate=SAMPLING_RATE, padding=True)

    # Create figures using the helper function
    ecg_fig = create_figure(time_window, ecg_filtered, 'ECG', 'red')
    ppg_fig = create_figure(time_window, ppg_filtered, 'PPG', 'lightblue')

    return ecg_fig, ppg_fig, new_index  # Return the new index to update the store

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
    start_index = current_index
    end_index = current_index + WINDOW_SIZE
    ecg_window = ecg_df['ECG'].iloc[start_index:end_index]

    heart_rate = calculate_heart_rate(ecg_window)
    spo2 = np.random.randint(92, 100)
    respiratory_rate = np.random.randint(12, 20)
    body_temp = temp_df['Temp'].iloc[start_index % len(temp_df)]
    heart_rate_color, spo2_color, respiratory_rate_color, body_temp_color = check_vital_signs(
        heart_rate, spo2, respiratory_rate, body_temp)

    return (
        f"{heart_rate:.1f} bpm", f"{spo2} %", f"{respiratory_rate} /min", f"{body_temp:.1f} °C",
        {'backgroundColor': heart_rate_color, 'color': 'white', 'fontWeight': 'bold'},
        {'backgroundColor': spo2_color, 'color': 'white', 'fontWeight': 'bold'},
        {'backgroundColor': respiratory_rate_color, 'color': 'white', 'fontWeight': 'bold'},
        {'backgroundColor': body_temp_color, 'color': 'white', 'fontWeight': 'bold'}
    )

if __name__ == '__main__':
    app.run_server(debug=True)
