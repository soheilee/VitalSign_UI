import random

import dash
from dash import dcc, html, Input, Output
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import dash_bootstrap_components as dbc
import collections

from numpy.core.defchararray import title

from alarm_engine import check_vital_signs
import sys

class Constants:
    port = 'COM9'
    baud_rate = 9600
    sampling_rate = 500
    window_size = 5*sampling_rate

class GUI():
    def __init__(self):
        super().__init__()
        self.xticks = collections.deque(maxlen=Constants.window_size)
        self.ecg = None
        self.ppg = None
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG, dbc.icons.BOOTSTRAP],
                             meta_tags=[{'name': 'viewport',
                                         'content': 'width=device-width, initial-scale=1.0'}])

    def set_layout(self):
        # create Cardas
        card_button = dbc.Card(
            dbc.CardBody([
                html.Button('Record', id='btn_record', n_clicks=0, style={'marginLeft': '30%'})
            ])
        )
        card_pulse = dbc.Card(
            dbc.CardBody([
                html.H3(
                    [html.I(className='bi bi-heart-pulse me-2')
                     ], className='text-danger'
                ),
                html.H3(id='heart-rate-value', children='')
            ], style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
        )
        card_respiration = dbc.Card(
            dbc.CardBody([
                html.H3(
                    [html.I(className='bi bi-lungs me-2')
                     ], className='text-primary'
                ),
                html.H3(id='respiratory-rate-value', children='')
            ],style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
        )
        card_spO2 = dbc.Card(
            dbc.CardBody([
                html.H3(
                    [html.I(className='bi bi-0-square-fill me-2')
                     ], className='text-primary'
                ),
                html.H3(id='spo2-value', children='')
            ],style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
        )
        card_temp = dbc.Card(
            dbc.CardBody([
                html.H3(
                    [html.I(className='bi bi-thermometer-half me-2')
                     ], className='text-success'
                ),
                html.H3(id='body-temp-value', children='')
            ],style={'fontSize': '60px', 'color': 'white', 'fontWeight': 'bold'})
        )

        main_card = dbc.Card(dbc.CardBody([
            dcc.Interval(id='interval-component-graphs', interval=100, n_intervals=0),
            dcc.Interval(id='interval-component-vitals', interval=1000, n_intervals=0),
            dbc.Row([
                dbc.Col(html.H1('VitalSign',
                                className='text-center text-success mb-2'))
            ],style={'margin-left': 1, 'margin-right': 1, 'margin-bottom': 1, 'margin-top': 2}),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='ecg-plot',figure={}, config={'displayModeBar': False})
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='ppg-plot', figure={}, config={'displayModeBar': False}),
                            dcc.Slider(0, 20, 1, value=10, id='my-slider')
                            ])
                        ])
                ], width=10),
                dbc.Col([
                    dbc.Row(card_button),
                    dbc.Row(card_pulse),
                    dbc.Row(card_respiration),
                    dbc.Row(card_spO2),
                    dbc.Row(card_temp)
                ]),
            ], style={'margin-left': 1, 'margin-right': 1, 'margin-bottom': 2, 'margin-top': 1}, justify='around')]
        ))

        layout = dbc.Container([main_card],
            fluid=True)
        return layout

    def setup_callbacks(self):
        @self.app.callback(
            [Output('ecg-plot', 'figure'),
             Output('ppg-plot', 'figure')],
             Input('interval-component-graphs', 'n_intervals')
        )

        def update_graphs(n):
            #if len(ecg) < 10:
             #   return None, None

            xticks = np.array(self.xticks)
            ecg_fig = go.Figure()
            ecg_fig.add_trace(go.Scatter(x=xticks, y=self.ecg, mode='lines', name='ECG', line=dict(color='red', width=5)))
            ecg_fig.update_layout(title='ECG', plot_bgcolor='black', paper_bgcolor='black', font_color='white')

            ppg_fig = go.Figure()
            ppg_fig.add_trace(go.Scatter(x=xticks, y=self.ppg, mode='lines', name='PPG', line=dict(color='lightblue', width=5)))
            ppg_fig.update_layout(title='PPG', plot_bgcolor='black', paper_bgcolor='black', font_color='white')
            return ecg_fig, ppg_fig

        @self.app.callback(
            [Output('heart-rate-value', 'children'),
             Output('spo2-value', 'children'),
             Output('respiratory-rate-value', 'children'),
             Output('body-temp-value', 'children')],
             Input('interval-component-vitals', 'n_intervals')
        )
        def update_vital_signs(n):

            heart_rate = np.random.randint(42, 140)
            spo2 = np.random.randint(92, 100)
            respiratory_rate = np.random.randint(12, 20)
            body_temp = np.random.randint(34, 40)

            #heart_rate_color, spo2_color, respiratory_rate_color, body_temp_color = check_vital_signs(
             #   heart_rate, spo2, respiratory_rate, body_temp)

            return (
                f"{heart_rate:.1f} bpm", f"{spo2} %", f"{respiratory_rate} /min", f"{body_temp:.1f} °C"
            )

    def run_soheil(self):
        self.app.run(debug=True, use_reloader=False)
