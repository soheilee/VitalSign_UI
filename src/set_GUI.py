import dash
import numpy as np
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
from alarm_engine import check_vital_signs  # For alarm checks


class Soheil():
    def __init__(self):
        super().__init__()
        self.app = dash.Dash(__name__)

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
    def setup_callbacks(self, ecg, ppg):
        @self.app.callback(
            [Output('ecg-plot', 'figure'),
             Output('ppg-plot', 'figure')],
            [Input('interval-component-graphs', 'n_intervals')]
        )

        def update_graphs(n):
            if len(ecg) < 10:
                return None, None

            xticks = np.array(self.xticks)

            ecg_fig = go.Figure()
            ecg_fig.add_trace(go.Scatter(x=xticks, y=ecg, mode='lines', name='ECG', line=dict(color='red', width=5)))
            ecg_fig.update_layout(title='ECG', plot_bgcolor='black', paper_bgcolor='black', font_color='white')

            ppg_fig = go.Figure()
            ppg_fig.add_trace(go.Scatter(x=xticks, y=ppg, mode='lines', name='PPG', line=dict(color='lightblue', width=5)))
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
    def run_soheil(self):
        self.app.run_server(debug=True, use_reloader=False)