import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash import no_update
from utils.ui_elements import make_gauge
from dash.dependencies import Input, Output, State
from app import app


from sqlalchemy import create_engine, text, Table, desc, select
from sqlalchemy.sql.schema import MetaData

import plotly.express as px
import pandas as pd


@app.callback(
    Output('temp_gauge', 'figure'),
    Output('humidity_gauge', 'figure'),
    Output('sunlight_graph', 'figure'),
    Output('plant1_graph', 'figure'),
    Output('plant2_graph', 'figure'),
    Output('plant3_graph', 'figure'),
    Output('plant4_graph', 'figure'),
    # The arguments below likely don't have to be updated every iteration in order to save computation.
    # To facilitate this, we can pass dash.no_update
    Output('plant1_name', 'children'),
    Output('plant2_name', 'children'),
    Output('plant3_name', 'children'),
    Output('plant4_name', 'children'),
    Output('plant1_humidity', 'children'),
    Output('plant2_humidity', 'children'),
    Output('plant3_humidity', 'children'),
    Output('plant4_humidity', 'children'),
    Output('plant1_humidity_target', 'children'),
    Output('plant2_humidity_target', 'children'),
    Output('plant3_humidity_target', 'children'),
    Output('plant4_humidity_target', 'children'),
    Output('plant1_lastwatered', 'children'),
    Output('plant2_lastwatered', 'children'),
    Output('plant3_lastwatered', 'children'),
    Output('plant4_lastwatered', 'children'),
    Input('update_page', 'n_intervals')
)
def update_page(n_intervals):
    engine = create_engine("sqlite+pysqlite:///garden.db", future=True)
    metadata = MetaData()
    sample_table = Table("sample", metadata, autoload_with=engine)
    sensor_table = Table("sensor", metadata, autoload_with=engine)
    plant_table = Table("plant", metadata, autoload_with=engine)
    error = 0
    humidity_result, temp_result, light_result, plant_graph_result, plant_misc = (None, None, None, None, None)
    with engine.connect() as conn:
        try:
            # get current ambient humidity
            humidity_result = conn.execute(
                select([sample_table.c.value]).select_from(sample_table).where(sample_table.c.sensor_id == sensor_table.c.id, sensor_table.c.type == 'ambient_humidity').limit(1).order_by(desc(sample_table.c.timestamp))
            ).fetchall()
            # get current temperature
            temp_result = conn.execute(
                select([sample_table.c.value]).where(sample_table.c.sensor_id == sensor_table.c.id, sensor_table.c.type == 'ambient_temperature').limit(1).order_by(desc(sample_table.c.timestamp))
            ).fetchall()
            # get last 100 light entries
            light_result= conn.execute(
                select([sample_table.c.value]).where(sample_table.c.sensor_id == sensor_table.c.id, sensor_table.c.type == 'light').limit(100).order_by(desc(sample_table.c.timestamp))
            ).fetchall()
            # get plant humidity graphs
            plant_graph_result = conn.execute(
                select([sample_table.c.value, sample_table.c.timestamp, plant_table.c.id]).where(sample_table.c.sensor_id == plant_table.c.humidity_sensor_id).limit(100).group_by(plant_table.c.id).order_by(desc(sample_table.c.timestamp))
            ).fetchall() # do I even need the join plant table? What sort of structure does this return? Looks like it returns a tuple of length 3.. hopefully grouped by plant.
            # we should be able to just get the plant_humidity and plant_last_watered from this plant_graph_result.
            plant_misc = conn.execute(
                select([plant_table.c.name, plant_table.c.target])
            ).fetchall() # we should get 4 tuples back of name, target
                # get plant names
                # get plant_humidity_target
            print(plant_misc)

        except Exception as e:
            print(e)
            error = 1
    if error == 1 or None in [humidity_result, temp_result, light_result, plant_graph_result, plant_misc]: # pass test values if there was an error
        print("Error occurred collecting DB data, passing test values")
        return [make_gauge("Temperature", 50, "° F", [0, 100], "#dc3545"), make_gauge("Relative Humidity", 50, "%", [0, 100], "#17a2b8"),
         px.line(pd.DataFrame({'timestamp':[1,2,3,4],'sunlight':[2,3,4,5]}), x='timestamp', y='sunlight', title='Test Input', width=525, height=250),
         px.line(pd.DataFrame({'timestamp':[1,2,3,4], 'humidity':[2,3,4,5]}), x='timestamp', y='humidity', width=450, height=300),
         px.line(pd.DataFrame({'timestamp':[1,2,3,4], 'humidity':[2,3,4,5]}), x='timestamp', y='humidity', width=450, height=300),
         px.line(pd.DataFrame({'timestamp':[1,2,3,4], 'humidity':[2,3,4,5]}), x='timestamp', y='humidity', width=450, height=300),
         px.line(pd.DataFrame({'timestamp':[1,2,3,4], 'humidity':[2,3,4,5]}), x='timestamp', y='humidity', width=450, height=300),
         "plant1 test value", "plant2 test value", "plant3 test value", "plant4 test value", "50", "50", "50", "50", "50", "50", "50", "50",
         "12:20:00 4/20/2021", "12:20:00 4/20/2021", "12:20:00 4/20/2021", "12:20:00 4/20/2021"]


    sunlight_df = pd.DataFrame(light_result, columns=["timestamp","value"])
    plant1_df = pd.DataFrame(plant_graph_result[0], columns=["timestamp", "value"])
    plant2_df = pd.DataFrame(plant_graph_result[1], columns=["timestamp", "value"])
    plant3_df = pd.DataFrame(plant_graph_result[2], columns=["timestamp", "value"])
    plant4_df = pd.DataFrame(plant_graph_result[3], columns=["timestamp", "value"])
    return [make_gauge("Temperature", temp_result[0]["value"], "° F", [0, 100], "#dc3545"), make_gauge("Relative Humidity", humidity_result[0]["value"], "%", [0, 100], "#17a2b8"), 
     px.line(sunlight_df, x='timestamp', y=sunlight_df.value, title='Sunlight', width=525, height=250),
     px.line(plant1_df, x='timestamp', y=plant1_df.value, width=450, height=300),
     px.line(plant2_df, x='timestamp', y=plant2_df.value, width=450, height=300),
     px.line(plant3_df, x='timestamp', y=plant3_df.value, width=450, height=300),
     px.line(plant4_df, x='timestamp', y=plant4_df.value, width=450, height=300), # plant humidity graphs
     plant_misc[0][0], plant_misc[1][0], plant_misc[2][0], plant_misc[3][0], #names
     # plant humidities, under the assumption that groupby puts them into another group array based on the plant: ith plant, 0th entry, 0th value (humidity)
     plant_graph_result[0][0][0], plant_graph_result[1][0][0], plant_graph_result[2][0][0], plant_graph_result[3][0][0],
     # plant humidity targets
     plant_misc[0][1], plant_misc[1][1], plant_misc[2][1], plant_misc[3][1],
     # plant_lastwatered, ith plant, most recent entry (0th), 1st value (timestamp)
     plant_graph_result[0][0][1], plant_graph_result[1][0][1], plant_graph_result[2][0][1], plant_graph_result[3][0][1]]


layout = [
    html.Div(
        [
            html.H1("Overview", className="card-header"),
            html.Div(
                [
                    html.H2("Ambient", className="card-title"),
                    html.Div(
                        [
                            dcc.Graph(id='temp_gauge', figure=make_gauge("Temperature", 0, "° F", [0, 100], "#dc3545"), className="col-sm-3"),
                            dcc.Graph(id='humidity_gauge', figure=make_gauge("Relative Humidity", 0, "%", [0, 100], "#17a2b8"), className="col-sm-3 mt-1"),
                            dcc.Graph(id='sunlight_graph', className="col-md-4 mt-1")
                        ],
                        className="row align-items-center",
                        id="data_div"
                    ),
                    dcc.Interval(
                                    id='update_page',
                                    interval=10*1000, # in milliseconds
                                    n_intervals=0
                            )
                ],
                className="card-body"
            ),
            html.Div(
                [
                    html.H2("Watering", className="card-title"),
                    html.Div(
                        [   
                            html.Div(
                                [
                                    html.H5(children='plant1', id="plant1_name", className="mt-3"),
                                    dbc.InputGroup([
                                        html.H5("Last Watered:"),
                                        html.H5(children="test", id="plant1_lastwatered", className="col align-self-end"),
                                    ]),
                                    dbc.InputGroup([
                                        html.H5("Soil Humidity:"),
                                        html.H5(children="test", id="plant1_humidity", className="col align-self-end"),
                                    ]),
                                    dbc.InputGroup([
                                        html.H5("Soil Humidity Target:"),
                                        html.H5(children="test", id="plant1_humidity_target", className="col align-self-end"),
                                    ]),
                                    dcc.Graph(id='plant1_graph', figure=px.line(pd.DataFrame({'timestamp':[1,2,3,4],'humidity':[2,3,4,5]}), x='timestamp', y='humidity', width=450, height=300))
                                ], className="col m-3 border",
                            ),
                            html.Div(
                                [
                                    html.H5(children='plant2', id="plant2_name", className="mt-3"),
                                    dbc.InputGroup([
                                        html.H5("Last Watered:"),
                                        html.H5(children="test", id="plant2_lastwatered", className="col align-self-end"),
                                    ]),
                                    dbc.InputGroup([
                                        html.H5("Soil Humidity:"),
                                        html.H5(children="test", id="plant2_humidity", className="col align-self-end"),
                                    ]),
                                    dbc.InputGroup([
                                        html.H5("Soil Humidity Target:"),
                                        html.H5(children="test", id="plant2_humidity_target", className="col align-self-end"),
                                    ]),
                                    dcc.Graph(id='plant2_graph', figure=px.line(pd.DataFrame({'timestamp':[1,2,3,4],'humidity':[2,3,4,5]}), x='timestamp', y='humidity', width=450, height=300))
                                ], className="col m-3 border"
                            ),
                        ],
                        className="row"
                    ),
                    html.Div(
                        [   
                            html.Div(
                                [
                                    html.H5(children='plant3', id="plant3_name", className="card-text mt-3"),
                                    dbc.InputGroup([
                                        html.H5("Last Watered:"),
                                        html.H5(children="test", id="plant3_lastwatered", className="col align-self-end"),
                                    ]),
                                    dbc.InputGroup([
                                        html.H5("Soil Humidity:"),
                                        html.H5(children="test", id="plant3_humidity", className="col align-self-end"),
                                    ]),
                                    dbc.InputGroup([
                                        html.H5("Soil Humidity Target:"),
                                        html.H5(children="test", id="plant3_humidity_target", className="col align-self-end"),
                                    ]),
                                    dcc.Graph(id='plant3_graph', figure=px.line(pd.DataFrame({'timestamp':[1,2,3,4],'humidity':[2,3,4,5]}), x='timestamp', y='humidity', width=450, height=300))
                                ], className="col m-3 border"
                            ),
                            html.Div(
                                [
                                    html.H5(children='plant4', id="plant4_name", className="mt-3"),
                                    dbc.InputGroup([
                                        html.H5("Last Watered:"),
                                        html.H5(children="test", id="plant4_lastwatered", className="col align-self-end"),
                                    ]),
                                    dbc.InputGroup([
                                        html.H5("Soil Humidity:"),
                                        html.H5(children="test", id="plant4_humidity", className="col align-self-end"),
                                    ]),
                                    dbc.InputGroup([
                                        html.H5("Soil Humidity Target:"),
                                        html.H5(children="test", id="plant4_humidity_target", className="col align-self-end"),
                                    ]),
                                    dcc.Graph(id='plant4_graph', figure=px.line(pd.DataFrame({'timestamp':[1,2,3,4],'humidity':[2,3,4,5]}), x='timestamp', y='humidity', width=450, height=300))
                                ], className="col m-3 border"
                            ),
                        ],
                        className="row"
                    )
                ],
                className="card-body"
            )
        ],
        className="card m-2"
    )

]

