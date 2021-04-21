import dash
import paho.mqtt.publish as publish
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app
from apps import configuration, controls, history, overview
import sys
import json

pumps = ["pump1", "pump2", "pump3", "pump4"]

layout = [
    html.Div([
        html.H1("Controls", className="card-header"),
        html.H3("Manual Water", className="card-title"),
        dbc.InputGroup([
            html.H4("Pump 1", className="card-title"),
            dcc.Input(id="pump1_time", type="number"),
            html.H5("Seconds", className="card-text")
        ], className="col md-3"),
        dbc.InputGroup([
            html.H4("Pump 2", className="card-title"),
            dcc.Input(id="pump2_time", type="number"),
            html.H5("Seconds", className="card-text")
        ], className="col md-3"),
        dbc.InputGroup([
            html.H4("Pump 3", className="card-title"),
            dcc.Input(id="pump3_time", type="number"),
            html.H5("Seconds", className="card-text")
        ], className="col md-3"),
        dbc.InputGroup([
            html.H4("Pump 4", className="card-title"),
            dcc.Input(id="pump4_time", type="number"),
            html.H5("Seconds", className="card-text")
        ], className="col md-3"),
        html.Div([
            html.H5(id="command_status"),
            html.Button('Clear',
                        id='clear',
                        className="button",
                        style={"margin": "20px"},
                        n_clicks=0),
            html.Button('Perform Operation',
                        id='control_pumps',
                        className="button",
                        style={"margin": "20px"},
                        n_clicks=0)
        ],
                 className="row",
                 style={
                     "padding-bottom": "10px",
                     "padding-left": "600px"
                 })
    ],
             className="card m-1")
]

app.config['suppress_callback_exceptions'] = True


@app.callback([
    Output('pump1_time', 'value'),
    Output('pump2_time', 'value'),
    Output('pump3_time', 'value'),
    Output('pump4_time', 'value')
], Input('clear', 'n_clicks'))
def clear_form(n_clicks):
    return 0, 0, 0, 0


@app.callback(Output('command_status', 'children'),
              Input('control_pumps', 'n_clicks'), State('pump1_time', 'value'),
              State('pump2_time', 'value'), State('pump3_time', 'value'),
              State('pump4_time', 'value'))
def perform_pump(n_clicks, pump1, pump2, pump3, pump4):
    if n_clicks > 0:
        if pump1 > 0:
            publish.single(
                "pumps/control/1",
                payload=json.dumps({"duration":pump1}),
                qos=2,
                retain=False,
                hostname=
                sys.argv[1],  ## TODO: Change hostname to be accurate
                port=1883)
        if pump2 > 0:
            publish.single(
                "pumps/control/2",
                payload=json.dumps({"duration":pump2}),
                qos=2,
                retain=False,
                hostname=
                sys.argv[1],  ## TODO: Change hostname to be accurate
                port=1883)
        if pump3 > 0:
            publish.single(
                "pumps/control/3",
                payload=json.dumps({"duration":pump3}),
                qos=2,
                retain=False,
                hostname=
                sys.argv[1],  ## TODO: Change hostname to be accurate
                port=1883)
        if pump4 > 0:
            publish.single(
                "pumps/control/4",
                payload=json.dumps({"duration":pump4}),
                qos=2,
                retain=False,
                hostname=
                sys.argv[1],  ## TODO: Change hostname to be accurate
                port=1883)
        return "Performing manual pump.."
    return ""