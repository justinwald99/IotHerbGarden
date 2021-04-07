import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

from app import app

plants = {'PlantId1', 'PlantId2', 'PlantId3', 'PlantId4'}
sensors = {'Sensor1','Sensor2','Sensor3', 'Sensor4'}
pumps = {'Pump1', 'Pump2', 'Pump3', 'Pump4'}
rates = {'second', 'minute', 'hour'}

layout = [
    html.H1("Configuration", className="card-header"),
    dcc.Tabs([
        dcc.Tab(label='Plants', children=[
            html.Div(
            [
                dcc.Dropdown(
                    id='plantDropdown',
                    options=[{'label':plantId, 'value':plantId} for plantId in plants],
                    value=None
                )
            ],
                style = {"width":"25%", "padding-top":"10px", "padding-bottom":"10px"}),
            html.Div(
            [
                html.H3("Parameters", className="card-title"),
                html.Div(
                [
                    html.Div([
                        html.H5("Name", className="card-title", style={"width":"25%"}),
                        dcc.Input(id="name", type="text", placeholder="getFromDB", style={"width":"25%"})
                    ],className='row'),
                    html.Div([
                        html.H5("Humidity Sensor", className="card-title", style={"width":"25%"}),
                        dcc.Dropdown(
                            id='humiditySensor',
                            options=[{'label':sensor, 'value':sensor} for sensor in sensors],
                            value=None,
                            style={"width":"50%"}
                        )
                    ],className='row'),
                    html.Div([
                        html.H5("Pump", className="card-title", style={"width":"25%"}),
                        dcc.Dropdown(
                            id='pump',
                            options=[{'label':pump, 'value':pump} for pump in pumps],
                            value=None,
                            style={"width":"50%"}
                        )
                    ],className='row'),
                    html.Div([
                        html.H5("Target Humidity", className="card-title", style={"width":"25%"}),
                        dcc.Input(id="targetHumidity", type="number", placeholder=0, min=0, max=100, style={"width":"25%"}),
                        html.H5("%", className="card-text", style={"padding-left":"10px"})
                    ],className='row'),
                    html.Div([
                        html.H5("Watering Cooldown", className="card-title", style={"width":"25%"}),
                        dcc.Input(id="wateringCooldown", type="number", placeholder=0, min=0, style={"width":"25%"}),
                        html.H5("Seconds", className="card-text", style={"padding-left":"10px"})
                    ],className='row'),
                    html.Div([
                        html.H5("Watering Duration", className="card-title", style={"width":"25%"}),
                        dcc.Input(id="wateringDuration", type="number", placeholder=0, min=0, style={"width":"25%"}),
                        html.H5("Seconds", className="card-text", style={"padding-left":"10px"})
                    ],className='row'),
                    html.Div([
                        html.H5("Humidity Tolerance", className="card-title", style={"width":"25%"}),
                        dcc.Input(id="humidityTolerance", type="number", placeholder=0, min=0, max=100, style={"width":"25%"}),
                        html.H5("+/- %", className="card-text", style={"padding-left":"10px"})
                    ],className='row'),
                ],
                className="card-body")
            ]),
            html.Div([
                html.Button('Cancel', id='cancel_plants', n_clicks=0, style={"position":"fixed", "right":"25%"}),
                html.Button('Save', id='save_plants', n_clicks=0, style={"position":"fixed", "right":"20%"}),
                html.Div(id='plants_out', style={"position":"fixed", "right":"30%"})
            ])
        ]),
        dcc.Tab(label='Sensors', children=[
            html.Div(
            [
                dcc.Dropdown(
                    id='sensorDropdown',
                    options=[{'label':sensorId, 'value':sensorId} for sensorId in sensors],
                    value=None
                )
            ],
                style = {"width":"25%", "padding-top":"10px", "padding-bottom":"10px"}),
            html.Div(
            [
                html.H3("Parameters", className="card-title"),
                html.Div(
                [
                    html.Div([
                        html.H5("Name", className="card-title", style={"width":"25%"}),
                        dcc.Input(id="sensorName", type="text", placeholder="getFromDB", style={"width":"25%"})
                    ],className='row'),
                    html.Div([
                        html.H5("sensor_name", className="card-title", style={"width":"25%"}),
                        dcc.Dropdown(
                            id='sensor_name',
                            options=[{'label':sensor, 'value':sensor} for sensor in sensors],
                            value=None,
                            style={"width":"50%"}
                        )
                    ],className='row'),
                    html.Div([
                        html.H5("Samples", className="card-title", style={"width":"25%"}),
                        dcc.Input(id="samples", type="number", placeholder=0, min=0, style={"width":"25%"}),
                        html.H5("per", className="card-text", style={"padding-left":"10px", "padding-right":"10px", "padding-top":"10px"}),
                        dcc.Dropdown(
                            id='rate',
                            options=[{'label':rate, 'value':rate} for rate in rates],
                            value=None,
                            style={"width":"40%"}
                        )
                    ],className='row'),
                ],
                className="card-body")
            ]),
            html.Div([
                html.Button('Cancel', id='cancel_sensors', n_clicks=0, style={"position":"fixed", "right":"25%"}),
                html.Button('Save', id='save_sensors', n_clicks=0, style={"position":"fixed", "right":"20%"}),
                html.Div(id='sensors_out', style={"position":"fixed", "right":"30%"})
            ])

        ])
    ])
]

@app.callback(
    Output('plantDropdown', 'value'),
    Output('name', 'value'),
    Output('humiditySensor', 'value'),
    Output('pump', 'value'),
    Output('targetHumidity', 'value'),
    Output('wateringCooldown', 'value'),
    Output('wateringDuration', 'value'),
    Output('humidityTolerance', 'value'),
    Output('save_plants', 'n_clicks'),
    Input('cancel_plants', 'n_clicks')
)
def cancelPlants(n_clicks):
    return None, '', None, None, 0, 0, 0, 0, 0

@app.callback(
    Output('plants_out', 'children'),
    Input('save_plants', 'n_clicks')
)
def savePlants(n_clicks):
    ## TODO error check the form data
    ## TODO mqtt message with all plant data from form
    if (n_clicks > 0): return html.H5("Plants saved", id="plants_out_text")
    return None

@app.callback(
    Output('sensorDropdown', 'value'),
    Output('sensorName', 'value'),
    Output('sensor_name', 'value'),
    Output('samples', 'value'),
    Output('rate', 'value'),
    Output('save_sensors', 'n_clicks'),
    Input('cancel_sensors', 'n_clicks')
)
def cancelSensors(n_clicks):
    return None, '', None,  0, None, 0

@app.callback(
    Output('sensors_out', 'children'),
    Input('save_sensors', 'n_clicks')
)
def saveSensors(n_clicks):
    ## TODO error check the form data
    ## TODO mqtt message with all sensor data from form
    if (n_clicks > 0): return html.H5("Sensors saved", id="sensors_out_text")
    return None