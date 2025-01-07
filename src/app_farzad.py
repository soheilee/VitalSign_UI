import time

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import serial
import threading
import collections
from alarm_engine import check_vital_signs  # For alarm checks

DEBUG = False
class Constants:
    port = 'COM9'
    baud_rate = 9600
    sampling_rate = 500
    window_size = 5*sampling_rate

class DashApp:
    def __init__(self,):
        # Serial port setup
        if DEBUG:
            self.ser = serial.Serial(Constants.port, Constants.baud_rate, write_timeout=0)
            self.ser.close()
            self.ser.open()
        else:
            ecg_df = pd.read_csv('../data/ECG.csv', header=None, names=['ECG'])
            ppg_df = pd.read_csv('../data/PPG.csv', header=None, names=['PPG'])
            self.ecg_array = ecg_df.to_numpy().reshape(-1)
            self.ppg_array = ppg_df.to_numpy().reshape(-1)
            self.ecg_idx = 0
            self.ppg_idx = 0

        self.data_buffer = collections.deque(maxlen=Constants.window_size)
        self.xticks      = collections.deque(maxlen=Constants.window_size)
        self.ecg_buffer = collections.deque(maxlen=Constants.window_size)
        self.ppg_buffer = collections.deque(maxlen=Constants.window_size)

        self.setup_serial_thread()
        self.xplot_idx = 0

        # Dash app setup
        self.app = dash.Dash(__name__)
        self.app.layout = self.create_layout()
        self.setup_callbacks()

    def setup_serial_thread(self):
        # Start serial reading in a separate thread
        serial_thread = threading.Thread(target=self.read_serial)
        serial_thread.daemon = True
        serial_thread.start()

    def read_serial(self):
        while True:
            if DEBUG:
                line = self.ser.read(self.ser.in_waiting).decode('utf-8').strip()
                if line:
                    self.data_buffer.append(float(line))
                    if len(self.xticks)==0:
                        last_tick = 0
                    else:
                        last_tick = self.xticks[-1] + 1/Constants.sampling_rate
                    self.xticks.append(last_tick)
                    # Todo filter self.ecg_filtered
            else:
                if len(self.xticks) == 0:
                    last_tick = 0
                else:
                    last_tick = self.xticks[-1] + 1 / Constants.sampling_rate
                self.xticks.append(last_tick)
                self.ecg_buffer.append(self.ecg_array[self.ecg_idx])
                self.ppg_buffer.append(self.ppg_array[self.ppg_idx])
                self.ecg_idx = (self.ecg_idx + 1) % len(self.ecg_array)
                self.ppg_idx = (self.ppg_idx + 1) % len(self.ppg_array)
                self.ecg_filtered = list(self.ecg_buffer)
                self.ppg_filtered = list(self.ppg_buffer)
                time.sleep(0.01)

    def create_layout(self):
        return html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
            dcc.Interval(id='interval-component-graphs', interval=50, n_intervals=0),
            dcc.Interval(id='interval-component-vitals', interval=1000, n_intervals=0),
            html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(5, 1fr)', 'gap': '10px'}, children=[
                html.Div(
                    style={'gridColumn': 'span 4', 'gridRow': 'span 2', 'border': '1px solid white', 'padding': '10px'},
                    children=[dcc.Graph(id='ecg-plot', config={'displayModeBar': False})]),
                html.Div(id='heart-rate-container', style={'border': '1px solid white', 'padding': '10px'}, children=[
                    html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                        html.H3("♥", style={'color': 'red', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                        html.Div(id='heart-rate-value',
                                 style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
                    ])
                ]),
                html.Div(id='respiratory-rate-container', style={'border': '1px solid white', 'padding': '10px'},
                         children=[
                             html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                                 html.H3("🌬️", style={'color': 'white', 'fontSize': '60px', 'margin': '0 10px 0 0'}),
                                 html.Div(id='respiratory-rate-value',
                                          style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
                             ])
                         ]),
                html.Div(
                    style={'gridColumn': 'span 4', 'gridRow': 'span 2', 'border': '1px solid white', 'padding': '10px'},
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
                        html.Div(id='body-temp-value',
                                 style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
                    ])
                ]),
            ]),
        ])
    def setup_callbacks(self):
        @self.app.callback(
            [Output('ecg-plot', 'figure'),
             Output('ppg-plot', 'figure')],
            [Input('interval-component-graphs', 'n_intervals')]
        )
        def update_graphs(n):
            if len(self.ecg_filtered) < 10:
                return None, None

            xticks = np.array(self.xticks)

            ecg_fig = go.Figure()
            ecg_fig.add_trace(go.Scatter(x=xticks, y=self.ecg_filtered, mode='lines', name='ECG', line=dict(color='red', width=5)))
            ecg_fig.update_layout(title='ECG', plot_bgcolor='black', paper_bgcolor='black', font_color='white')

            ppg_fig = go.Figure()
            ppg_fig.add_trace(go.Scatter(x=xticks, y=self.ppg_filtered, mode='lines', name='PPG', line=dict(color='lightblue', width=5)))
            ppg_fig.update_layout(title='PPG', plot_bgcolor='black', paper_bgcolor='black', font_color='white')
            return ecg_fig, ppg_fig

        @self.app.callback(
            [Output('heart-rate-value', 'children'),
             Output('spo2-value', 'children'),
             Output('respiratory-rate-value', 'children'),
             Output('body-temp-value', 'children'),
             Output('heart-rate-container', 'style'),
             Output('spo2-container', 'style'),
             Output('respiratory-rate-container', 'style'),
             Output('body-temp-container', 'style')],
            [Input('interval-component-vitals', 'n_intervals')]
        )
        def update_vital_signs(n):

            heart_rate = np.random.randint(42, 140)
            spo2 = np.random.randint(92, 100)
            respiratory_rate = np.random.randint(12, 20)
            body_temp = np.random.randint(34, 40)

            heart_rate_color, spo2_color, respiratory_rate_color, body_temp_color = check_vital_signs(
                heart_rate, spo2, respiratory_rate, body_temp)

            return (
                f"{heart_rate:.1f} bpm", f"{spo2} %", f"{respiratory_rate} /min", f"{body_temp:.1f} °C",
                {'backgroundColor': heart_rate_color, 'color': 'white', 'fontWeight': 'bold'},
                {'backgroundColor': spo2_color, 'color': 'white', 'fontWeight': 'bold'},
                {'backgroundColor': respiratory_rate_color, 'color': 'white', 'fontWeight': 'bold'},
                {'backgroundColor': body_temp_color, 'color': 'white', 'fontWeight': 'bold'}
            )
    def run(self):
        self.app.run_server(debug=True, use_reloader=False)


if __name__ == '__main__':
    my_app = DashApp()  # Adjust port and baud rate as needed
    my_app.run()
