import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


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
            "height": 100,
            "margin": {
                "l": 5,
                "r": 5,
                "t": 5,
                "b": 5
            }
        }
    )


def history_graph():
    df = pd.read_csv("data/example_data.csv")
    fig = go.Figure()
    for sensor in df["sensor_name"].unique():
        sensor_df = df.loc[df['sensor_name'] == sensor]
        fig.add_trace(go.Scatter(x=sensor_df["timestamp"], y=sensor_df["value"]))
    return fig
