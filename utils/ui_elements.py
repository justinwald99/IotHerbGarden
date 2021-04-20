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


def history_graph():
    engine = create_engine("sqlite+pysqlite:///garden.db", future=True)
    metadata = MetaData()
    sample_table = Table("sample", metadata, autoload_with=engine)
    sensor_table = Table("sensor", metadata, autoload_with=engine)
    with engine.connect() as conn:
        data = conn.execute(
            select(sample_table.c.timestamp, sensor_table.c.name, sample_table.c.value, sensor_table.c.unit).
            join_from(sample_table, sensor_table).limit(100)
        ).fetchall()
    if not data:
        return go.Figure()
    df = pd.DataFrame(
        data, columns=["timestamp", "sensor_name", "value", "unit"])
    print(df)

    fig = px.line(df, x="timestamp", y=df.value,
                  line_group="sensor_name", color="sensor_name", template="seaborn")
    return fig
