import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import Table, create_engine, select
from sqlalchemy.sql.schema import MetaData


def make_gauge(title, value, suffix, range, color):
    return go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            gauge={
                "axis": {
                    "visible": False,
                    "range": range
                },
                "bar": {
                    "color": color
                }
            },
            title={
                "text": title,
                "font":
                {
                    "size": 10
                }
            },
            number={
                "suffix": suffix
            }
        ),
        layout={
            "height": 150,
            "margin": {
                "l": 5,
                "r": 5,
                "t": 5,
                "b": 5
            }
        }
    )
