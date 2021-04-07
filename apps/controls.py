import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from app import app
from apps import configuration, controls, history, overview

layout = [
    html.Div(
        [
            html.H1("Controls", className="card-header"),
            html.Div(
                [
                    html.H3("Manual Water", className="card-title"),
                ],
                className = "col"
            ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("Pump 1", className="card-title")
                            ],
                            className="",
                            style={
                               "text-align":"left"
                            }
                        ),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    options=[
                                        {'label': '0', 'value': 0},
                                        {'label': '1', 'value': 1},
                                        {'label': '2', 'value': 2},
                                        {'label': '3', 'value': 3},
                                        {'label': '4', 'value': 4},
                                        {'label': '5', 'value': 5},
                                        {'label': '6', 'value': 6},
                                        {'label': '7', 'value': 7},
                                        {'label': '8', 'value': 8},
                                        {'label': '9', 'value': 9},
                                        {'label': '10', 'value': 10},
                                    ],
                                    id = "pump1_time",
                                    value="0"
                                )
                            ]
                        ),
                        html.Div(
                            [
                                html.H5("Seconds", className = "card-text" ),
                            ],
                            className=""
                        )
                    ],
                    className = "row",
                    style={
                            "padding-bottom":"10px",
                            "padding-left":"30px"
                    }
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("Pump 2", className="card-title")
                            ],
                            className="",
                            style={
                               "text-align":"left"
                            }
                        ),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    options=[
                                        {'label': '0', 'value': 0},
                                        {'label': '1', 'value': 1},
                                        {'label': '2', 'value': 2},
                                        {'label': '3', 'value': 3},
                                        {'label': '4', 'value': 4},
                                        {'label': '5', 'value': 5},
                                        {'label': '6', 'value': 6},
                                        {'label': '7', 'value': 7},
                                        {'label': '8', 'value': 8},
                                        {'label': '9', 'value': 9},
                                        {'label': '10', 'value': 10},
                                    ],
                                    id = "pump2_time",
                                    value="0"
                                )
                            ],
                            className="",
                        ),
                        html.Div(
                            [
                                html.H5("Seconds", className = "card-text" ),
                            ],
                            className=""
                        )
                    ],
                    className = "row",
                    style={
                            "padding-bottom":"10px",
                            "padding-left":"30px"
                    }
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("Pump 3", className="card-title")
                            ],
                            className="",
                            style={
                               "text-align":"left"
                            }
                        ),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    options=[
                                        {'label': '0', 'value': 0},
                                        {'label': '1', 'value': 1},
                                        {'label': '2', 'value': 2},
                                        {'label': '3', 'value': 3},
                                        {'label': '4', 'value': 4},
                                        {'label': '5', 'value': 5},
                                        {'label': '6', 'value': 6},
                                        {'label': '7', 'value': 7},
                                        {'label': '8', 'value': 8},
                                        {'label': '9', 'value': 9},
                                        {'label': '10', 'value': 10},
                                    ],
                                    id = "pump3_time",
                                    value="0"
                                )
                            ],
                            className="",
                        ),
                        html.Div(
                            [
                                html.H5("Seconds", className = "card-text" ),
                            ],
                            className=""
                        )
                    ],
                    className = "row",
                    style={
                            "padding-bottom":"10px",
                            "padding-left":"30px"
                    }
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("Pump 4", className="card-title")
                            ],
                            className="",
                            style={
                               "text-align":"left"
                            }
                        ),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    options=[
                                        {'label': '0', 'value': 0},
                                        {'label': '1', 'value': 1},
                                        {'label': '2', 'value': 2},
                                        {'label': '3', 'value': 3},
                                        {'label': '4', 'value': 4},
                                        {'label': '5', 'value': 5},
                                        {'label': '6', 'value': 6},
                                        {'label': '7', 'value': 7},
                                        {'label': '8', 'value': 8},
                                        {'label': '9', 'value': 9},
                                        {'label': '10', 'value': 10},
                                    ],
                                    id = "pump4_time",
                                    value="0"
                                )
                            ],
                            className="",
                        ),
                        html.Div(
                            [
                                html.H5("Seconds", className = "card-text" ),
                            ],
                            className=""
                        )
                    ],
                    className = "row",
                    style={
                            "padding-bottom":"10px",
                            "padding-left":"30px"
                    }
                ),
                html.Div(
                    [   
                        html.H5(id="command_status"),
                        html.Button('Clear', id='clear', className="button", style={"margin":"20px"}, n_clicks=0),
                        html.Button('Perform Operation', id='control_pumps', className="button", style={"margin":"20px"}, n_clicks=0)
                    ],
                    className="row",
                    style={
                        "padding-bottom":"10px",
                        "padding-left":"600px"
                    }
                )
    ],
    className = "card m-1"
    )
]

app.config['suppress_callback_exceptions'] = True
@app.callback(
    [Output('pump1_time', 'value'),
    Output('pump2_time', 'value'),
    Output('pump3_time', 'value'),
    Output('pump4_time', 'value')],
    Input('clear', 'n_clicks'))
def clear_form(n_clicks):
    return 0, 0, 0, 0

@app.callback(
    Output('command_status', 'children'),
    Input('control_pumps', 'n_clicks'),
    Input('pump1_time', 'value'),
    Input('pump2_time', 'value'),
    Input('pump3_time', 'value'),
    Input('pump4_time', 'value'))
def perform_pump(n_clicks, pump1, pump2, pump3, pump4):
    if n_clicks > 0:
        ## TODO: PERFORM MQTT REQUEST BASED ON VALUES, if MQTT fails return an error message
        return "Performing manual pump.."
    return ""