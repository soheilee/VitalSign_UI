import dash
from dash import dcc, html
import dash.dependencies as dd
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os
from scipy.signal import butter, filtfilt

# Import external processing engines
from heart_rate_engine import calculate_heart_rate  # For heart rate calculation
from alarm_engine import check_vital_signs  # For alarm checks

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Vital Signs Monitoring System"

# Load data
ecg_df = pd.read_csv('../data/ECG.csv', header=None, names=['ECG'])
ppg_df = pd.read_csv('../data/PPG.csv', header=None, names=['PPG'])
temp_df = pd.read_csv('../data/TEMP.csv', header=None, names=['Temp'])

# Generate time series (1 ms per step)
sampling_rate = 250  # 250 Hz sampling rate
time_series = np.arange(0, len(ecg_df) * (1 / sampling_rate), 1 / sampling_rate)

# Define a sliding window size
window_size = 1000  # Display 1 second of data at 250 Hz

# Define layout
app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    dcc.Interval(id='interval-component-graphs', interval=50, n_intervals=0),
    dcc.Interval(id='interval-component-vitals', interval=1000, n_intervals=0),
    html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(5, 1fr)', 'gap': '10px'}, children=[
        html.Div(style={'gridColumn': 'span 4', 'gridRow': 'span 2', 'border': '1px solid white', 'padding': '10px'},
                 children=[dcc.Graph(id='ecg-plot', config={'displayModeBar': False})]),
        html.Div(id='heart-rate-container', style={'border': '1px solid white', 'padding': '10px'}, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("♥", style={'color': 'red', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='heart-rate-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
            ])
        ]),
        html.Div(id='respiratory-rate-container', style={'border': '1px solid white', 'padding': '10px'}, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🌬️", style={'color': 'white', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='respiratory-rate-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
            ])
        ]),
        html.Div(style={'gridColumn': 'span 4', 'gridRow': 'span 2', 'border': '1px solid white', 'padding': '10px'},
                 children=[dcc.Graph(id='ppg-plot', config={'displayModeBar': False})]),
        html.Div(id='spo2-container', style={'border': '1px solid white', 'padding': '10px'}, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🫁", style={'color': 'white', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='spo2-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
            ])
        ]),
        html.Div(id='body-temp-container', style={'border': '1px solid white', 'padding': '10px'}, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.H3("🌡️", style={'color': 'white', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                html.Div(id='body-temp-value', style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
            ])
        ]),
    ]),
])

# Global index to keep track of streaming data
current_index = 0


# Filter function
def low_pass_filter(signal, cutoff_freq, sampling_rate, order=4, padding=True):
    nyquist = 0.5 * sampling_rate
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)

    if padding:
        pad_len = 3 * max(len(b), len(a))
        padded_signal = np.concatenate([signal[pad_len - 1::-1], signal, signal[:-pad_len - 1:-1]])
        filtered_signal = filtfilt(b, a, padded_signal)
        return filtered_signal[pad_len:-pad_len]
    else:
        return filtfilt(b, a, signal)


@app.callback(
    [dd.Output('ecg-plot', 'figure'),
     dd.Output('ppg-plot', 'figure')],
    [dd.Input('interval-component-graphs', 'n_intervals')]
)
def update_graphs(n):
    global current_index, ecg_df, ppg_df, time_series, window_size

    start_index = current_index
    end_index = current_index + window_size
    if end_index > len(ecg_df):
        end_index = len(ecg_df)
        start_index = end_index - window_size
        if start_index < 0:
            start_index = 0

    current_index = (current_index + 10) % len(ecg_df)

    ecg_window = ecg_df['ECG'].iloc[start_index:end_index].to_numpy()
    ppg_window = ppg_df['PPG'].iloc[start_index:end_index].to_numpy()
    time_window = time_series[start_index:end_index]

    ecg_filtered = low_pass_filter(ecg_window, cutoff_freq=40, sampling_rate=sampling_rate, padding=True)
    ppg_filtered = low_pass_filter(ppg_window, cutoff_freq=5, sampling_rate=sampling_rate, padding=True)

    ecg_fig = go.Figure()
    ecg_fig.add_trace(go.Scatter(x=time_window, y=ecg_filtered, mode='lines', name='ECG', line=dict(color='red', width=5)))
    ecg_fig.update_layout(title='ECG', plot_bgcolor='black', paper_bgcolor='black', font_color='white')

    ppg_fig = go.Figure()
    ppg_fig.add_trace(go.Scatter(x=time_window, y=ppg_filtered, mode='lines', name='PPG', line=dict(color='lightblue', width=5)))
    ppg_fig.update_layout(title='PPG', plot_bgcolor='black', paper_bgcolor='black', font_color='white')

    return ecg_fig, ppg_fig


@app.callback(
    [dd.Output('heart-rate-value', 'children'),
     dd.Output('spo2-value', 'children'),
     dd.Output('respiratory-rate-value', 'children'),
     dd.Output('body-temp-value', 'children'),
     dd.Output('heart-rate-container', 'style'),
     dd.Output('spo2-container', 'style'),
     dd.Output('respiratory-rate-container', 'style'),
     dd.Output('body-temp-container', 'style')],
    [dd.Input('interval-component-vitals', 'n_intervals')]
)
def update_vital_signs(n):
    global current_index, ecg_df, ppg_df, temp_df

    start_index = current_index
    end_index = current_index + window_size
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