import dash
from dash_bootstrap_components._components.InputGroup import InputGroup
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_html_components as html
from sqlalchemy.sql import annotation
from sqlalchemy.sql.elements import between, or_
from app import app
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import Table, create_engine, select
from sqlalchemy.sql.schema import MetaData
import pandas as pd
from dash.exceptions import PreventUpdate
import datetime as dt
from time import perf_counter

engine = create_engine("sqlite+pysqlite:///garden.db", future=True)
metadata = MetaData()
sample_table = Table("sample", metadata, autoload_with=engine)
sensor_table = Table("sensor", metadata, autoload_with=engine)
plant_table = Table("plant", metadata, autoload_with=engine)
watering_table = Table("watering_event", metadata, autoload_with=engine)

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
                                    {"label": "Soil Humidity", "value": "soil_humidity"},
                                    {"label": "Humidity Target", "value": "humidity_target"},
                                    {"label": "Pump Activated", "value": "pump_activated"}
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


def get_plant_traces(plant_ids, fields):
    """Generate the traces for plant specific sensors."""
    # Get plant data
    traces = []
    with engine.connect() as conn:
        for plant_id in plant_ids:
            result = conn.execute(
                select(sample_table.c.timestamp, sensor_table.c.name, sample_table.c.value, sensor_table.c.unit, plant_table.c.target)
                .join_from(sample_table, sensor_table)
                .join_from(sensor_table, plant_table)
                .order_by(sample_table.c.timestamp.desc())
                .where(between(sample_table.c.timestamp, data_start, dt.datetime.now()))
                .where(plant_table.c.id == plant_id)
            ).fetchall()
            data = pd.DataFrame(result, columns=["timestamp", "sensor_name", "value", "unit", "target"])
            if "soil_humidity" in fields:
                traces.append(go.Scattergl(
                    x=data["timestamp"],
                    y=data["value"],
                    name=data["sensor_name"][0] + " Soil Humidity"))

            if "humidity_target" in fields:
                traces.append(go.Scattergl(
                    x=data["timestamp"],
                    y=data["target"],
                    name=data["sensor_name"][0] + " Humidity Target"))
    return traces


def add_watering_events(plant_ids, figure):
    """Add shaded regions for watering events to a figure."""
    with engine.connect() as conn:
        for plant_id in plant_ids:
            result = conn.execute(
                select(watering_table.c.timestamp, watering_table.c.duration, plant_table.c.name)
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
                select(sample_table.c.timestamp, sensor_table.c.name, sample_table.c.value, sensor_table.c.unit)
                .join_from(sample_table, sensor_table)
                .order_by(sample_table.c.timestamp.desc())
                .where(between(sample_table.c.timestamp, data_start, dt.datetime.now()))
                .where(sensor_table.c.id == sensor_id)
            ).fetchall()
            data = pd.DataFrame(result, columns=["timestamp", "sensor_name", "value", "unit"])
            traces.append(go.Scattergl(x=data["timestamp"], y=data["value"], name=data["sensor_name"][0]))
    return traces


@app.callback(Output("history_graph", "figure"),
              Input("ambient_options", "value"),
              Input("plant_options", "value"),
              Input("field_options", "value"),
              Input('history_graph', 'relayoutData'))
def draw_graph(ambient_options, plant_options, fields, relay_out_data):
    """Draw the history graph for the first time"""

    # Update the amount of data cleared if the user wants data older than current value.
    global data_start
    if (relay_out_data and "xaxis.range[0]" in relay_out_data.keys() and
        dt.datetime.fromisoformat(relay_out_data["xaxis.range[0]"]) < data_start):
        data_start = dt.datetime.fromisoformat(relay_out_data["xaxis.range[0]"])

    elif (relay_out_data and "xaxis.range[0]" in relay_out_data.keys()):
        raise PreventUpdate

    print(dash.callback_context.triggered)

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


@app.callback(Output("ambient_options", "options"),
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


@app.callback(Output("plant_options", "options"),
              Output("plant_options", "value"),
              Input("page-content", "children"))
def load_plants(children):
    """Load list of plants for checkbox."""
    with engine.connect() as conn:
        data = conn.execute(
            select(plant_table.c.id, plant_table.c.name)
        ).fetchall()
    return ([{"label": name, "value": id} for id, name in data], [id for id, name in data])

