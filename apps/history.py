import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
from app import app
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import Table, create_engine, select
from sqlalchemy.sql.schema import MetaData
from utils.ui_elements import history_graph
import pandas as pd

layout = [
    dcc.Interval(
        id='interval-component',
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
                                options=[
                                    {'label': 'New York City', 'value': 'NYC'},
                                    {'label': 'Montréal', 'value': 'MTL'},
                                    {'label': 'San Francisco', 'value': 'SF'}
                                ],
                                value=[],
                                labelStyle={"display": "block"}
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
                                options=[
                                    {'label': 'New York City', 'value': 'NYC'},
                                    {'label': 'Montréal', 'value': 'MTL'},
                                    {'label': 'San Francisco', 'value': 'SF'}
                                ],
                                value=[],
                                labelStyle={"display": "block"}
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
                                    {'label': 'New York City', 'value': 'NYC'},
                                    {'label': 'Montréal', 'value': 'MTL'},
                                    {'label': 'San Francisco', 'value': 'SF'}
                                ],
                                value=[],
                                labelStyle={"display": "block"}
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
                figure=go.Figure()
            )
        ],
        className="card my-2 p-2"
    )
]


@app.callback(Output('history_graph', 'figure'),
              Input('page-content', 'children'))
def draw_graph(n):
    """Pull new data from the database to update the graph."""
    return history_graph()

@app.callback(Output('history_graph', 'extend_data'),
              Input('interval-component', 'n_intervals'))
def update_graph(n):
    """Update the graph as new data is collected."""
    engine = create_engine("sqlite+pysqlite:///garden.db", future=True)
    metadata = MetaData()
    sample_table = Table("sample", metadata, autoload_with=engine)
    sensor_table = Table("sensor", metadata, autoload_with=engine)

    with engine.connect() as conn:
        data = conn.execute(
            select(sample_table.c.timestamp, sensor_table.c.name, sample_table.c.value, sensor_table.c.unit).
            join_from(sample_table, sensor_table).limit(100)
        ).fetchall()

    return data
    
