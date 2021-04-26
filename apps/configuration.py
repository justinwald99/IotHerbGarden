import json
import logging
import time

import colorama
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from app import app
from colorama import Fore
from dash import callback_context, no_update
from dash.dependencies import Input, Output, State
from garden_manager import client
from sqlalchemy import select
from utils.db_interaction import engine, plant_table, sensor_table

pump_list = [
    (1, "pump_1"),
    (2, "pump_2"),
    (3, "pump_3"),
    (4, "pump_4")
]

rates = ["second", "minute", "hour"]

rate_mapping = {
    "second": 1,
    "minute": 60,
    "hour": 3600
}

# Init color engine
colorama.init()

# Logging setup
mqtt_logger = logging.getLogger(Fore.MAGENTA + "mqtt_log")

logging.basicConfig(
    level="INFO", format=f"{Fore.CYAN}%(asctime)s {Fore.RESET}%(name)s {Fore.YELLOW}%(levelname)s {Fore.RESET}%(message)s")


def get_plant_ids():
    """Return the ids of plants in the database."""
    with engine.connect() as conn:
        result = conn.execute(
            select(plant_table.c.id, plant_table.c.name)
        ).fetchall()
    return [{"label": name, "value": id} for id, name in result]


def get_soil_humidity_sensors():
    """Get a list of soil_humidity sensors."""
    with engine.connect() as conn:
        result = conn.execute(
            select(sensor_table.c.id, sensor_table.c.name)
            .where(sensor_table.c.type == "soil_humidity")
        ).fetchall()
    return [{"label": name, "value": id} for id, name in result]


def get_all_sensors():
    """Get a list of all sensors."""
    with engine.connect() as conn:
        result = conn.execute(
            select(sensor_table.c.id, sensor_table.c.name)
        ).fetchall()
    return [{"label": name, "value": id} for id, name in result]


layout = [
    html.H1("Configuration"),
    dbc.Tabs([
        dbc.Tab(label="Plants", children=[
            html.Div(
                [
                    dbc.Select(
                        id="selectedPlant",
                        options=get_plant_ids()
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
                                dcc.Input(id="name", type="text",
                                          className="col-md-3")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Humidity Sensor",
                                        className="col-md-3"),
                                dbc.Select(
                                    id="humiditySensor",
                                    options=get_soil_humidity_sensors(),
                                    className="col-md-3"
                                )
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Pump", className="col-md-3"),
                                dbc.Select(
                                    id="pump",
                                    options=[{"label": name, "value": id}
                                             for id, name in pump_list],
                                    className="col-md-3"
                                )
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Target Humidity",
                                        className="col-md-3"),
                                dcc.Input(id="targetHumidity", type="number", min=0, max=100,
                                          className="col-md-3"),
                                html.H5("%", className="px-2")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Watering Cooldown",
                                        className="col-md-3"),
                                dcc.Input(
                                    id="wateringCooldown", type="number", min=0, className="col-md-3"),
                                html.H5("Seconds", className="px-2")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Watering Duration",
                                        className="col-md-3"),
                                dcc.Input(
                                    id="wateringDuration", type="number", min=0, className="col-md-3"),
                                html.H5("Seconds", className="px-2")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Humidity Tolerance",
                                        className="col-md-3"),
                                dcc.Input(id="humidityTolerance", type="number",
                                          min=0, max=50, className="col-md-3"),
                                html.H5("+/- %", className="px-2")
                            ], className="py-2"),
                            html.Span([
                                dbc.Button(
                                    "Cancel", id="cancel_plants", n_clicks=0),
                                dbc.Button(
                                    "Save", id="save_plants", n_clicks=0),
                                html.H5(id="plants_out")
                            ], className="offset-md-9")
                        ],
                        className="card-body")
                ],
                className="card"),
        ]),
        dbc.Tab(label="Sensors", children=[
            html.Div(
                [
                    dbc.Select(
                        id="selectedSensor",
                        options=get_all_sensors()
                    )
                ], className="col-md-3 m-4"),
            html.Div(
                [
                    html.H3("Parameters", className="card-header"),
                    html.Div(
                        [
                            dbc.InputGroup([
                                html.H5("Name", className="col-md-3"),
                                dcc.Input(id="sensor_label",
                                          type="text", className="col-md-3")
                            ], className="py-2"),
                            dbc.InputGroup([
                                html.H5("Samples", className="col-md-3"),
                                dcc.Input(id="samples", type="number",
                                          min=0, className="col-md-3"),
                                html.H5("per", className="px-2"),
                                dbc.Select(
                                    id="rate",
                                    options=[{"label": rate, "value": rate}
                                             for rate in rates],
                                    className="col-md-3"
                                )
                            ], className="py-2"),
                            html.Div([
                                dbc.Button(
                                    "Cancel", id="cancel_sensors", n_clicks=0),
                                dbc.Button(
                                    "Save", id="save_sensors", n_clicks=0),
                                html.H5(id="sensors_out")
                            ], className="offset-md-9")
                        ],
                        className="card-body")
                ], className="card"),
        ])
    ])
]


@app.callback(
    Output("name", "value"),
    Output("humiditySensor", "value"),
    Output("pump", "value"),
    Output("targetHumidity", "value"),
    Output("wateringCooldown", "value"),
    Output("wateringDuration", "value"),
    Output("humidityTolerance", "value"),
    Input("selectedPlant", "value"),
    Input("cancel_plants", "n_clicks")
)
def load_plant_config(selected_plant, n_clicks):
    """Load the existing config for the selected plant."""
    caller = callback_context.triggered[0]["prop_id"]

    if caller == "selectedPlant.value" and selected_plant:
        with engine.connect() as conn:
            result = conn.execute(
                select(plant_table, sensor_table.c.name)
                .join(sensor_table, sensor_table.c.id)
                .where(plant_table.c.id == selected_plant)
            ).fetchone()
        id, name, sensor_id, pump_id, target, cooldown, duration, tolerance, sensor_name = result
        return name, sensor_id, pump_id, target, cooldown, duration, tolerance

    return "", None, None, 0, 0, 0, 0


@app.callback(
    Output("plants_out", "children"),
    Output("selectedPlant", "options"),
    Input("save_plants", "n_clicks"),
    State("selectedPlant", "value"),
    State("name", "value"),
    State("humiditySensor", "value"),
    State("pump", "value"),
    State("targetHumidity", "value"),
    State("wateringCooldown", "value"),
    State("wateringDuration", "value"),
    State("humidityTolerance", "value")
)
def savePlants(n_clicks, selectedPlant, name, humidity_sensor_id, pump_id, target,
               watering_cooldown, watering_duration, humidity_tolerance):
    """Save the plant config to the database."""
    if (n_clicks > 0):
        payload = {
            "id": int(selectedPlant),
            "name": name,
            "humidity_sensor_id": int(humidity_sensor_id),
            "pump_id": pump_id,
            "target": target,
            "watering_cooldown": watering_cooldown,
            "watering_duration": watering_duration,
            "humidity_tolerance": humidity_tolerance
        }
        client.publish(f"plants/config", payload=json.dumps(payload), qos=2)

        mqtt_logger.info(
            f"Published to /plants/config: {json.dumps(payload, indent=4)}")

        # Wait for the plant to be updated
        time.sleep(1)

        return html.H5("Plants saved", id="plants_out_text"), get_plant_ids()

    return no_update, no_update


@ app.callback(
    Output("sensor_label", "value"),
    Output("samples", "value"),
    Output("rate", "value"),
    Input("selectedSensor", "value"),
    Input("cancel_sensors", "n_clicks")
)
def load_sensor_config(selected_sensor, n_clicks):
    """Load the current config for the selected sensor from the DB."""
    caller = callback_context.triggered[0]["prop_id"]
    if caller == "selectedSensor.value" and selected_sensor:
        with engine.connect() as conn:
            result = conn.execute(
                select(sensor_table)
                .where(sensor_table.c.id == selected_sensor)
            ).fetchone()
        id, type, name, unit, sample_gap = result

        for unit, unit_length in rate_mapping.items():
            unit_amount = unit_length / sample_gap
            if unit_amount.is_integer():
                return name, unit_amount, unit
    return None, "",  0


@ app.callback(
    Output("sensors_out", "children"),
    Output("selectedSensor", "options"),
    Input("save_sensors", "n_clicks"),
    State("selectedSensor", "value"),
    State("sensor_label", "value"),
    State("samples", "value"),
    State("rate", "value")
)
def saveSensors(n_clicks, sensor_id, name, unit_amount, time_unit):
    if (n_clicks > 0):
        with engine.connect() as conn:

            sample_gap = rate_mapping[time_unit] / unit_amount

            # Load old sensor info because not all is known by frontend
            result = conn.execute(
                select(sensor_table.c.type, sensor_table.c.unit)
                .where(sensor_table.c.id == sensor_id)
            ).fetchone()
            type, unit = result
            payload = {
                "id": int(sensor_id),
                "type": type,
                "name": name,
                "unit": unit,
                "sample_gap": sample_gap
            }
            client.publish(f"sensors/config",
                           payload=json.dumps(payload), qos=2)

            mqtt_logger.info(
                f"Published to /sensors/config: {json.dumps(payload, indent=4)}")

            # Wait for the plant to be updated
            time.sleep(1)

            return html.H5("Sensor saved", id="sensors_out"), get_all_sensors()
    return no_update, no_update
