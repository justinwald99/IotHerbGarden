import dash_html_components as html
import dash_core_components as dcc
from utils.ui_elements import history_graph

layout = [
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
                figure=history_graph()
            )
        ],
        className="card my-2 p-2"
    )
]
