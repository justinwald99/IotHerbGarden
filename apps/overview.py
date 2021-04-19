import dash_html_components as html
import dash_core_components as dcc
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
    Input('update_page', 'n_intervals')
)
def update_page(n_intervals):
    engine = create_engine("sqlite+pysqlite:///garden.db", future=True)
    metadata = MetaData()
    test = 0
    humidity_result, temp_result, light_result = (None, None, None)
    with engine.connect() as conn:
        try:
            sample_table = Table("sample", metadata, autoload_with=engine)
            sensor_table = Table("sensor", metadata, autoload_with=engine)
            humidity_result = conn.execute(
                select(sample_table.c.value).where(sample_table.c.sensor_id == sensor_table.c.id, sensor_table.c.type == 'ambient_humidity').limit(1).order_by(desc(sample_table.c.timestamp))
            ).fetchall()
            temp_result = conn.execute(
                select(sample_table.c.value).where(sample_table.c.sensor_id == sensor_table.c.id, sensor_table.c.type == 'ambient_temperature').limit(1).order_by(desc(sample_table.c.timestamp))
            ).fetchall()
            light_result= conn.execute(
                select(sample_table.c.value).where(sample_table.c.sensor_id == sensor_table.c.id, sensor_table.c.type == 'light').limit(100).order_by(desc(sample_table.c.timestamp))
            ).fetchall()
        except:
            print("Error occurred collecting DB data, passing test values")
            test = 1
    if None in (humidity_result, temp_result, light_result) or test == 1:
        return [make_gauge("Temperature", 50, "° F", [0, 100], "#dc3545"), make_gauge("Relative Humidity", 50, "%", [0, 100], "#17a2b8"), px.line(pd.DataFrame({'timestamp':[1,2,3,4],'sunlight':[2,3,4,5]}), x='timestamp', y='sunlight', title='Test Input', width=525, height=250)]
    df = pd.DataFrame(light_result, columns=["timestamp","value"])
    return [make_gauge("Temperature", temp_result[0]["value"], "° F", [0, 100], "#dc3545"), make_gauge("Relative Humidity", humidity_result[0]["value"], "%", [0, 100], "#17a2b8"), 
        px.line(df, x='timestamp', y=df.value, title='Sunlight', width=525, height=250)]
    # only using the last result from the query

layout = [
    html.Div(
        [
            html.H1("Overview", className="card-header"),
            html.Div(
                [
                    html.H2("Ambient", className="card-title"),
                    html.Div(
                        [
                            dcc.Graph(id='temp_gauge', className="col-sm-3 mt-1"),
                            dcc.Graph(id='humidity_gauge', className="col-sm-3 mt-1"),
                            dcc.Graph(id='sunlight_graph', className="col-md-4 mt-1")
                        ],
                        className="row",
                        id="data_div"
                    ),
                    dcc.Interval(
                                    id='update_page',
                                    interval=10*1000, # in milliseconds
                                    n_intervals=0
                            )
                ],
                className="card-body"
            )
        ],
        className="card m-2"
    )

]
