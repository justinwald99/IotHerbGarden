import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
from app import app
from utils.ui_elements import history_graph

layout = [
    dcc.Interval(
        id='interval-component',
        interval=3*1000,  # in milliseconds
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
                id="history_graph"
            )
        ],
        className="card my-2 p-2"
    )
]


@app.callback(Output('history_graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_data(n):
    """Pull new data from the database to update the graph."""
    return history_graph()
