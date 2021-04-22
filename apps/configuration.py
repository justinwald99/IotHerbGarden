import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import callback_context, no_update
import paho.mqtt.publish as publish
import json
from app import app
import sys

from sqlalchemy import MetaData, create_engine, select, Table

# DB objects
engine = create_engine("sqlite+pysqlite:///garden.db", future=True)
metadata = MetaData()
plantTable = Table("plant", metadata, autoload_with=engine)
sensorTable = Table("sensor", metadata, autoload_with=engine)
with engine.connect() as conn:
        plantsData = conn.execute(select(
            plantTable.c.id,
            plantTable.c.name,
            plantTable.c.humidity_sensor_id,
            plantTable.c.pump_id,
            plantTable.c.target,
            plantTable.c.watering_cooldown,
            plantTable.c.watering_duration,
            plantTable.c.humidity_tolerance
        )).fetchall()
        sensorsData = conn.execute(select(
            sensorTable.c.id,
            sensorTable.c.type,
            sensorTable.c.name,
            sensorTable.c.unit,
            sensorTable.c.sample_gap
        )).fetchall()

def getDBData():
    with engine.connect() as conn:
        plantsData = conn.execute(select(
            plantTable.c.id,
            plantTable.c.name,
            plantTable.c.humidity_sensor_id,
            plantTable.c.pump_id,
            plantTable.c.target,
            plantTable.c.watering_cooldown,
            plantTable.c.watering_duration,
            plantTable.c.humidity_tolerance
        )).fetchall()
        sensorsData = conn.execute(select(
            sensorTable.c.id,
            sensorTable.c.type,
            sensorTable.c.name,
            sensorTable.c.unit,
            sensorTable.c.sample_gap
        )).fetchall()

#plants = ['PlantId1', 'PlantId2', 'PlantId3', 'PlantId4']
#sensors = ['Sensor1', 'Sensor2', 'Sensor3', 'Sensor4']
pumps = ['Pump1', 'Pump2', 'Pump3', 'Pump4']
rates = ['second', 'minute', 'hour']

rate_mapping = {
    'second': 1,
    'minute': 60,
    'hour': 3600
}

def get_plant_payload(id, name, humiditySensor, pump, targetHumidity, wateringCooldown, wateringDuration, humidityTolerance):
    return json.dumps({"id":id, "name":name, "sensor":humiditySensor, "pump":pump, "target":targetHumidity,
     "watering_cooldown":wateringCooldown, "watering_duration":wateringDuration, "humidity_tolerance":humidityTolerance})


layout = [
    html.H1("Configuration"),
    dbc.Tabs([
        dbc.Tab(label='Plants', children=[
            html.Div(
                [
                    dbc.Select(
                        id='selectedPlant',
                        options=[{'label': plant[1], 'value': list(plant)}
                                 for plant in plantsData]
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
                                dcc.Input(id="name", type="text", className="col-md-3")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Humidity Sensor", className="col-md-3"),
                                dbc.Select(
                                    id='humiditySensor',
                                    options=[{'label': sensor[2], 'value': sensor[0]} for sensor in sensorsData],
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
                                dcc.Input(id="targetHumidity", type="number", min=0, max=100,
                                          className="col-md-3"),
                                html.H5("%", className="px-2")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Watering Cooldown", className="col-md-3"),
                                dcc.Input(id="wateringCooldown", type="number", min=0, className="col-md-3"),
                                html.H5("Seconds", className="px-2")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Watering Duration", className="col-md-3"),
                                dcc.Input(id="wateringDuration", type="number", min=0, className="col-md-3"),
                                html.H5("Seconds", className="px-2")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Humidity Tolerance", className="col-md-3"),
                                dcc.Input(id="humidityTolerance", type="number", min=0, max=100, className="col-md-3"),
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
                        id='selectedSensor',
                        options=[{'label': sensor[2], 'value': list(sensor)} for sensor in sensorsData]
                    )
                ], className="col-md-3 m-4"),
            html.Div(
                [
                    html.H3("Parameters", className="card-header"),
                    html.Div(
                        [
                            dbc.InputGroup([
                                html.H5("Name", className="col-md-3"),
                                dcc.Input(id="sensor_label", type="text", className="col-md-3")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Samples", className="col-md-3"),
                                dcc.Input(id="samples", type="number", min=0, className="col-md-3"),
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
    Output('selectedPlant', 'value'),
    Output('name', 'value'),
    Output('humiditySensor', 'value'),
    Output('pump', 'value'),
    Output('targetHumidity', 'value'),
    Output('wateringCooldown', 'value'),
    Output('wateringDuration', 'value'),
    Output('humidityTolerance', 'value'),
    Output('save_plants', 'n_clicks'),
    Input('selectedPlant','value'),
    Input('cancel_plants', 'n_clicks')
)
def handlePlants(selectedPlant, n_clicks):
    ctx = callback_context
    caller = ctx.triggered[0]['prop_id'].split('.')[0]
    if caller == 'selectedPlant':
        if selectedPlant is not None:
            selectedPlant = selectedPlant.split(",")
            return no_update, selectedPlant[1], selectedPlant[2], selectedPlant[3], selectedPlant[4], selectedPlant[5], selectedPlant[6], selectedPlant[7], 0
    else:
        return None, '', None, None, 0, 0, 0, 0, 0


@app.callback(
    Output('plants_out', 'children'),
    Input('save_plants', 'n_clicks'),
    State('selectedPlant', 'value'), # save plant id
    State('name', 'value'), # save plant name
    State('humiditySensor', 'value'), # save humidity sensor
    State('pump', 'value'), # save pump
    State('targetHumidity', 'value'), #save target humidity
    State('wateringCooldown', 'value'), #save watering cooldown
    State('wateringDuration', 'value'), # save watering duration
    State('humidityTolerance', 'value') # save humidity tolerance
)
def savePlants(n_clicks, selectedPlant, name, humiditySensor, pump, targetHumidity, wateringCooldown, wateringDuration, humidityTolerance):
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
            selectedPlant = selectedPlant.split(",")
            publish.single(f"plants/config", payload=get_plant_payload(selectedPlant[0], name, humiditySensor, pump, targetHumidity, wateringCooldown, wateringDuration, humidityTolerance), 
                qos=2, retain=True, hostname=sys.argv[1], ## TODO: Change hostname to be accurate
                port=1883)
            getDBData()
            return html.H5("Plants saved", id="plants_out_text")
        else:
            return html.H5(invalidReturnString, id="plants_out_text")
    return None

@app.callback(
    Output('selectedSensor', 'value'),
    Output('sensor_label', 'value'),
    Output('samples', 'value'),
    Output('rate', 'value'),
    Output('save_sensors', 'n_clicks'),
    Input('selectedSensor', 'value'),
    Input('cancel_sensors', 'n_clicks')
)
def handleSensors(selectedSensor, n_clicks):
    ctx = callback_context
    caller = ctx.triggered[0]['prop_id'].split('.')[0]
    if caller == 'selectedSensor':
        if selectedSensor is not None:
            selectedSensor = selectedSensor.split(",")
            secondsBetweenSamples = int(selectedSensor[4])
            for rate in rates:
                samplesPerRate = rate_mapping[rate] / secondsBetweenSamples
                if (samplesPerRate.is_integer()):
                    return no_update, selectedSensor[2], samplesPerRate, rate, 0
            return no_update, selectedSensor[2], -1, rates[0], 0
    else:
        return None, '',  0, None, 0


@app.callback(
    Output('sensors_out', 'children'),
    Input('save_sensors', 'n_clicks'),
    State('selectedSensor', 'value'),
    State('sensor_label', 'value'),
    State('samples', 'value'),
    State('rate', 'value')
)
def saveSensors(n_clicks, selectedSensor, sensor_label, samples, rate):
    # TODO Autofill
    if (n_clicks > 0):
        if samples < 0:
            return html.H5("Invalid samples (>0)", id="sensors_out_text")
        time_between_samples = int(samples / rate_mapping[rate])
        selectedSensor = selectedSensor.split(",")
        publish.single(topic=f"sensors/config", payload=json.dumps({"id":selectedSensor[0], "type":selectedSensor[1], "name":sensor_label, "unit":selectedSensor[3], "sample_gap":time_between_samples}),
            qos=2, retain=True, hostname=sys.argv[1], port=1883)
        getDBData()
        return html.H5("Sensors saved", id="sensors_out_text")
    return None
