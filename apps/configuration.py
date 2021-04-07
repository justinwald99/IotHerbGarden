import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app

plants = {'PlantId1', 'PlantId2', 'PlantId3', 'PlantId4'}
sensors = {'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4'}
pumps = {'Pump1', 'Pump2', 'Pump3', 'Pump4'}
rates = {'second', 'minute', 'hour'}

layout = [
    html.H1("Configuration"),
    dbc.Tabs([
        dbc.Tab(label='Plants', children=[
            html.Div(
                [
                    dbc.Select(
                        id='plantDropdown',
                        options=[{'label': plantId, 'value': plantId}
                                 for plantId in plants]
                    )
                ],
                className="col-md-3 m-4"
            ),
            html.Div(
                [
                    html.H3("Parameters", className="card-header"),
                    html.Div(
                        [
                            dbc.InputGroup([
                                html.H5("Name", className="col-md-3"),
                                dcc.Input(id="name", type="text", placeholder="getFromDB", className="col-md-3")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Humidity Sensor", className="col-md-3"),
                                dbc.Select(
                                    id='humiditySensor',
                                    options=[{'label': sensor, 'value': sensor} for sensor in sensors],
                                    className="col-md-3"
                                )
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Pump", className="col-md-3"),
                                dbc.Select(
                                    id='pump',
                                    options=[{'label': pump, 'value': pump} for pump in pumps],
                                    className="col-md-3"
                                )
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Target Humidity", className="col-md-3"),
                                dcc.Input(id="targetHumidity", type="number", placeholder=0, min=0, max=100,
                                          className="col-md-3"),
                                html.H5("%", className="px-2")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Watering Cooldown", className="col-md-3"),
                                dcc.Input(id="wateringCooldown", type="number",
                                          placeholder=0, min=0, className="col-md-3"),
                                html.H5("Seconds", className="px-2")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Watering Duration", className="col-md-3"),
                                dcc.Input(id="wateringDuration", type="number",
                                          placeholder=0, min=0, className="col-md-3"),
                                html.H5("Seconds", className="px-2")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Humidity Tolerance", className="col-md-3"),
                                dcc.Input(id="humidityTolerance", type="number",
                                          placeholder=0, min=0, max=100, className="col-md-3"),
                                html.H5("+/- %", className="px-2")
                            ], className="py-2"),
                            html.Span([
                                dbc.Button('Cancel', id='cancel_plants', n_clicks=0),
                                dbc.Button('Save', id='save_plants', n_clicks=0),
                                html.H5(id='plants_out')
                            ], className="offset-md-9")
                        ],
                        className="card-body")
                ],
                className="card"),
        ]),
        dbc.Tab(label='Sensors', children=[
            html.Div(
                [
                    dbc.Select(
                        id='sensorDropdown',
                        options=[{'label': sensorId, 'value': sensorId} for sensorId in sensors]
                    )
                ], className="col-md-3 m-4"),
            html.Div(
                [
                    html.H3("Parameters", className="card-header"),
                    html.Div(
                        [
                            dbc.InputGroup([
                                html.H5("Name", className="col-md-3"),
                                dcc.Input(id="sensorName", type="text",
                                          placeholder="getFromDB", className="col-md-3")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("sensor_name", className="col-md-3"),
                                dbc.Select(
                                    id='sensor_name',
                                    options=[{'label': sensor, 'value': sensor} for sensor in sensors],
                                    className="col-md-3"
                                )
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Samples", className="col-md-3"),
                                dcc.Input(id="samples", type="number",
                                          placeholder=0, min=0, className="col-md-3"),
                                html.H5("per", className="px-2"),
                                dbc.Select(
                                    id='rate',
                                    options=[{'label': rate, 'value': rate} for rate in rates],
                                    className="col-md-3"
                                )
                            ], className="py-2"),
                            html.Div([
                                dbc.Button('Cancel', id='cancel_sensors', n_clicks=0),
                                dbc.Button('Save', id='save_sensors', n_clicks=0),
                                html.H5(id='sensors_out')
                            ], className="offset-md-9")
                        ],
                        className="card-body")
                ], className="card"),
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
    # TODO error check the form data
    # TODO mqtt message with all plant data from form
    if (n_clicks > 0):
        return html.H5("Plants saved", id="plants_out_text")
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
    # TODO error check the form data
    # TODO mqtt message with all sensor data from form
    if (n_clicks > 0):
        return html.H5("Sensors saved", id="sensors_out_text")
    return None
