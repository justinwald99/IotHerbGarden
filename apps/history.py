import datetime as dt
import re

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from app import app
from dash.dependencies import Input, Output
from sqlalchemy import between, select
from utils.db_interaction import (engine, plant_table, sample_table,
                                  sensor_table, watering_table)

history_graph = go.Figure()

# Earliest datetime to pull data from.
data_start = dt.datetime.now() - dt.timedelta(hours=4)

layout = [
    dcc.Interval(
        id="interval-component",
        interval=1*1000,  # in milliseconds
        n_intervals=0
    ),
    html.H1("History"),
    html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            "Ambient"
                        ],
                        className="card-subtitle"
                    ),
                    html.Div(
                        [
                            dcc.Checklist(
                                options=[],
                                value=[],
                                labelStyle={"display": "block"},
                                id="ambient_options"
                            )
                        ],
                        className="card-body"
                    )
                ],
                className="card p-2"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            "Plants"
                        ],
                        className="card-subtitle"
                    ),
                    html.Div(
                        [
                            dcc.Checklist(
                                options=[],
                                value=[],
                                labelStyle={"display": "block"},
                                id="plant_options"
                            )
                        ],
                        className="card-body"
                    )
                ],
                className="card p-2"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            "Fields"
                        ],
                        className="card-subtitle"
                    ),
                    html.Div(
                        [
                            dcc.Checklist(
                                options=[
                                    {"label": "Soil Humidity",
                                        "value": "soil_humidity"},
                                    {"label": "Humidity Target",
                                        "value": "humidity_target"},
                                    {"label": "Pump Activated",
                                        "value": "pump_activated"}
                                ],
                                value=["soil_humidity"],
                                labelStyle={"display": "block"},
                                id="field_options"
                            )
                        ],
                        className="card-body"
                    )
                ],
                className="card p-2"
            )
        ],
        className="card-deck"
    ),
    html.Div(
        [
            dcc.Graph(
                id="history_graph",
                figure=history_graph
            )
        ],
        className="card my-2 p-2"
    )
]


def set_start_date():
    """Set the global var start date based on the from_date specified by the user.

    Return true if data needs to be reloaded
    """
    # Update the amount of data cleared if the user wants data older than current value.
    global data_start

    triggered = dash.callback_context.triggered[0]

    # Reset start_date on fresh load.
    if triggered["prop_id"] == "history_graph.relayoutData" and triggered["value"] == {"autosize": True}:
        data_start = dt.datetime.now() - dt.timedelta(hours=12)
        return True

    if (triggered["prop_id"] == "history_graph.relayoutData" and
            "xaxis.range[0]" in triggered["value"].keys()):
        # Chop ms to conform to iso standard.
        date_str = re.match("\d{4}-\d{2}-\d{0,2} ?\d{0,2}:?\d{0,2}:?\d{0,2}",
                            triggered["value"]["xaxis.range[0]"]).group()
        from_date = dt.datetime.fromisoformat(date_str)

        if (from_date < data_start):
            data_start = from_date
            return True
        return False

    return False


def get_plant_traces(plant_ids, fields):
    """Generate the traces for plant specific sensors."""
    # Get plant data
    traces = []
    with engine.connect() as conn:
        for plant_id in plant_ids:
            result = conn.execute(
                select(sample_table.c.timestamp, sensor_table.c.name,
                       sample_table.c.value, sensor_table.c.unit, plant_table.c.target)
                .join_from(sample_table, sensor_table)
                .join_from(sensor_table, plant_table)
                .order_by(sample_table.c.timestamp.desc())
                .where(between(sample_table.c.timestamp, data_start, dt.datetime.now()))
                .where(plant_table.c.id == plant_id)
            ).fetchall()
            data = pd.DataFrame(
                result, columns=["timestamp", "sensor_name", "value", "unit", "target"])
            if "soil_humidity" in fields:
                traces.append(go.Scatter(
                    x=data["timestamp"],
                    y=data["value"],
                    name=data["sensor_name"][0] + " Soil Humidity"))

            if "humidity_target" in fields:
                traces.append(go.Scatter(
                    x=data["timestamp"],
                    y=data["target"],
                    name=data["sensor_name"][0] + " Humidity Target"))
    return traces


def add_watering_events(plant_ids, figure):
    """Add shaded regions for watering events to a figure."""
    with engine.connect() as conn:
        for plant_id in plant_ids:
            result = conn.execute(
                select(watering_table.c.timestamp,
                       watering_table.c.duration, plant_table.c.name)
                .join_from(watering_table, plant_table)
                .order_by(watering_table.c.timestamp.desc())
                .where(between(watering_table.c.timestamp, data_start, dt.datetime.now()))
                .where(plant_table.c.id == plant_id)
            ).fetchall()
            for timestamp, duration, name in result:
                figure.add_vrect(
                    x0=timestamp,
                    x1=timestamp + dt.timedelta(seconds=duration),
                    line_width=0, fillcolor="red", opacity=0.2)


def get_ambient_traces(selected_sensors):
    """Generate the traces for ambient sensors."""
    # Get ambient data
    traces = []
    with engine.connect() as conn:
        for sensor_id in selected_sensors:
            result = conn.execute(
                select(sample_table.c.timestamp, sensor_table.c.name,
                       sample_table.c.value, sensor_table.c.unit)
                .join_from(sample_table, sensor_table)
                .order_by(sample_table.c.timestamp.desc())
                .where(between(sample_table.c.timestamp, data_start, dt.datetime.now()))
                .where(sensor_table.c.id == sensor_id)
            ).fetchall()
            data = pd.DataFrame(
                result, columns=["timestamp", "sensor_name", "value", "unit"])
            traces.append(go.Scatter(
                x=data["timestamp"], y=data["value"], name=data["sensor_name"][0]))
    return traces


@app.callback(Output("history_graph", "figure"),
              Input("ambient_options", "value"),
              Input("plant_options", "value"),
              Input("field_options", "value"),
              Input('history_graph', 'relayoutData'))
def draw_graph(ambient_options, plant_options, fields, relay_out_data):
    """Draw the history graph for the first time"""
    update_required_triggers = ["ambient_options.value",
                                "plant_options.value", "field_options.value"]

    triggered = dash.callback_context.triggered
    triggered_ids = [x["prop_id"] for x in triggered]

    update_required = False
    for id in triggered_ids:
        if id in update_required_triggers:
            update_required = True

    # Set the start date, then update graph only if needed
    if not set_start_date() and not update_required:
        return dash.no_update

    fig = go.Figure()

    # Setup range slider
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="minute", stepmode="todate"),
                dict(count=20, label="20m", step="minute", stepmode="todate"),
                dict(count=1, label="1h", step="hour", stepmode="todate"),
                dict(count=8, label="8h", step="hour", stepmode="todate"),
                dict(count=1, label="1d", step="day", stepmode="todate"),
                dict(count=7, label="7d", step="day", stepmode="todate")
            ])
        )
    )

    fig.add_traces(get_ambient_traces(ambient_options))
    fig.add_traces(get_plant_traces(plant_options, fields))
    add_watering_events(plant_options, fig)

    return fig


@ app.callback(Output("ambient_options", "options"),
               Output("ambient_options", "value"),
               Input("page-content", "children"))
def load_ambient_sensors(children):
    """Load list of ambient sensors for checkbox."""
    ambient_sensor_types = ["ambient_temperature", "ambient_humidity", "light"]
    with engine.connect() as conn:
        data = conn.execute(
            select(sensor_table.c.id, sensor_table.c.name)
            .where(sensor_table.c.type.in_(ambient_sensor_types))
        ).fetchall()
    return ([{"label": name, "value": id} for id, name in data], [id for id, name in data])


@ app.callback(Output("plant_options", "options"),
               Output("plant_options", "value"),
               Input("page-content", "children"))
def load_plants(children):
    """Load list of plants for checkbox."""
    with engine.connect() as conn:
        data = conn.execute(
            select(plant_table.c.id, plant_table.c.name)
        ).fetchall()
    return ([{"label": name, "value": id} for id, name in data], [id for id, name in data])
