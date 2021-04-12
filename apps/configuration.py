import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import paho.mqtt.publish as publish
import json
from app import app

plants = ['PlantId1', 'PlantId2', 'PlantId3', 'PlantId4']
sensors = ['Sensor1', 'Sensor2', 'Sensor3', 'Sensor4']
pumps = ['Pump1', 'Pump2', 'Pump3', 'Pump4']
rates = ['second', 'minute', 'hour']

rate_mapping = {
    'second': 1,
    'minute': 60,
    'hour': 3600
}

# def get_mqtt_data() TODO: Auto-populate fields using MQTT

def get_plant_payload(name, humiditySensor, pump, targetHumidity, wateringCooldown, wateringDuration, humidityTolerance):
    return json.dumps({ "name":name, "sensor":humiditySensor, "pump":pump, "target":targetHumidity,
     "watering_cooldown":wateringCooldown, "watering_duration":wateringDuration, "humidity_tolerance":humidityTolerance})


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
                                dcc.Input(id="sensor_label", type="text",
                                          placeholder="getFromDB", className="col-md-3")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("sensor_id", className="col-md-3"),
                                dbc.Select(
                                    id='sensor_id',
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
    Input('save_plants', 'n_clicks'),
    State('plantDropdown', 'value'), # save plant id
    State('name', 'value'), # save plant name
    State('humiditySensor', 'value'), # save humidity sensor
    State('pump', 'value'), # save pump
    State('targetHumidity', 'value'), #save target humidity
    State('wateringCooldown', 'value'), #save watering cooldown
    State('wateringDuration', 'value'), # save watering duration
    State('humidityTolerance', 'value') # save humidity tolerance
)
def savePlants(n_clicks, plantDropdown, name, humiditySensor, pump, targetHumidity, wateringCooldown, wateringDuration, humidityTolerance):
    invalidReturnString = ""
    if (n_clicks > 0):
        if targetHumidity < 0 or targetHumidity > 100:
            invalidReturnString += "Invalid Target Humidity [0,100]\n"
        if wateringCooldown < 0:
            invalidReturnString += "Invalid Watering Cooldown >0\n"
        if wateringDuration <= 0 or wateringDuration > 5:
            invalidReturnString += "Invalid Watering Duration (0,5]\n"
        if humidityTolerance > 50 or humidityTolerance < 0:
            invalidReturnString += "Invalid Humidity Tolerance [0,50]\n"
        if invalidReturnString == "":
            publish.single(f"plants/config/{plantDropdown}", payload=get_plant_payload(name, humiditySensor, pump, targetHumidity, wateringCooldown, wateringDuration, humidityTolerance), 
                qos=2, retain=True, hostname="192.168.1.182", ## TODO: Change hostname to be accurate
                port=1883) ## TODO: note that the plantDropdown values probably don't store what we want it to
            return html.H5("Plants saved", id="plants_out_text")
        else:
            return html.H5(invalidReturnString, id="plants_out_text")
    return None


@app.callback(
    Output('sensorDropdown', 'value'),
    Output('sensor_label', 'value'),
    Output('sensor_id', 'value'),
    Output('samples', 'value'),
    Output('rate', 'value'),
    Output('save_sensors', 'n_clicks'),
    Input('cancel_sensors', 'n_clicks')
)
def cancelSensors(n_clicks):
    return None, '', None,  0, None, 0


@app.callback(
    Output('sensors_out', 'children'),
    Input('save_sensors', 'n_clicks'),
    State('sensorDropdown', 'value'),
    State('sensor_label', 'value'),
    State('sensor_id', 'value'),
    State('samples', 'value'),
    State('rate', 'value')
)
def saveSensors(n_clicks, sensorDropdown, sensor_label, sensor_id, samples, rate):
    # TODO Autofill
    if (n_clicks > 0):
        if samples < 0:
            return html.H5("Invalid samples (>0)", id="sensors_out_text")
        time_between_samples = samples / rate_mapping[rate]
        publish.single(topic=f"sensors/config/{sensorDropdown}", payload=json.dumps({"name":sensor_id, "sample_rate":time_between_samples}),
            qos=2, retain=True, hostname="192.168.1.182", port=1883)
         ## TODO: sensorDropdown probably isn't what we want here, but they're all the same type so I'm unsure of what to put for {type}
         ## also, what is the difference between sensor_label and sensor_id? I passed sensor_id to the payload, so change it if it's wrong :)
        return html.H5("Sensors saved", id="sensors_out_text")
    return None
