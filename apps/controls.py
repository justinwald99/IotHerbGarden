import json
import sys

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import paho.mqtt.publish as publish
from app import app
from dash.dependencies import Input, Output, State

pumps = ["pump1", "pump2", "pump3", "pump4"]

layout = [
    html.Div([
        html.H1("Controls", className="card-header"),
        html.Div([
            html.H3("Manual Water", className="card-title"),
            dbc.InputGroup([
                html.H4("Pump 1", className="px-2"),
                dcc.Input(id="pump1_time", type="number", className="px-2"),
                html.H5("Seconds", className="px-2")
            ], className="py-2"),
            dbc.InputGroup([
                html.H4("Pump 2", className="px-2"),
                dcc.Input(id="pump2_time", type="number", className="px-2"),
                html.H5("Seconds", className="px-2")
            ], className="py-2"),
            dbc.InputGroup([
                html.H4("Pump 3", className="px-2"),
                dcc.Input(id="pump3_time", type="number", className="px-2"),
                html.H5("Seconds", className="px-2")
            ], className="py-2"),
            dbc.InputGroup([
                html.H4("Pump 4", className="px-2"),
                dcc.Input(id="pump4_time", type="number", className="px-2"),
                html.H5("Seconds", className="px-2")
            ], className="py-2"),
            html.Div([
                html.H5(id="command_status"),
                dbc.Button('Clear', id='clear', className="px-2"),
                dbc.Button('Perform Operation',
                           id='control_pumps', className="px-2")
            ])
        ], className="card-body")
    ], className="card m-2")
]


@app.callback(
    Output('pump1_time', 'value'),
    Output('pump2_time', 'value'),
    Output('pump3_time', 'value'),
    Output('pump4_time', 'value'),
    Input('clear', 'n_clicks'))
def clear_form(n_clicks):
    return 0, 0, 0, 0


@app.callback(Output('command_status', 'children'),
              Input('control_pumps', 'n_clicks'),
              State('pump1_time', 'value'),
              State('pump2_time', 'value'),
              State('pump3_time', 'value'),
              State('pump4_time', 'value'))
def perform_pump(n_clicks, pump1, pump2, pump3, pump4):
    if n_clicks:
        if pump1:
            publish.single(
                "pumps/control/1",
                payload=json.dumps({"duration": pump1}),
                qos=2, hostname=sys.argv[1])
        if pump2:
            publish.single(
                "pumps/control/2",
                payload=json.dumps({"duration": pump2}),
                qos=2, hostname=sys.argv[1])
        if pump3:
            publish.single(
                "pumps/control/3",
                payload=json.dumps({"duration": pump3}),
                qos=2, hostname=sys.argv[1])
        if pump4:
            publish.single(
                "pumps/control/4",
                payload=json.dumps({"duration": pump4}),
                qos=2, hostname=sys.argv[1])
        return "Performing manual pump.."
    return dash.no_update
