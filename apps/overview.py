import dash_html_components as html
import dash_core_components as dcc
from utils.ui_elements import make_gauge
from dash.dependencies import Input, Output, State
from sqlalchemy import create_engine, text
from app import app
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


@app.callback(
    Output('temp_gauge', 'figure'),
    Output('humidity_gauge', 'figure'),
    Output('sunlight_graph', 'figure'),
    Input('update_page', 'n_intervals')
)
def update_page(n_intervals):
    conn = create_engine("sqlite+pysqlite:///garden.db", future=False).connect()
    try:
        humidity_result = conn.execute(text("SELECT TOP 1 value FROM sample INNER JOIN sensor ON sample.sensor_id = sensor.id WHERE type = N'ambient_humidity' ORDER BY sample.id DESC"))
        temp_result = conn.execute(text("SELECT TOP 1 value FROM sample INNER JOIN sensor ON sample.sensor_id = sensor.id WHERE type = N'ambient_temperature' ORDER BY sample.id DESC"))
        light_result= conn.execute(text("SELECT TOP 100 timestamp,value FROM sample INNER JOIN sensor ON sample.sensor_id = dbo.sensor.id WHERE type = N'light' ORDER BY sample.id DESC"))
    except:
        print("Error occurred collecting DB data, passing test values")
        return [make_gauge("Temperature", 50, "° F", [0, 100], "#dc3545"), make_gauge("Relative Humidity", 50, "%", [0, 100], "#17a2b8"), px.line(pd.DataFrame({'timestamp':[1,2,3,4],'sunlight':[2,3,4,5]}), x='timestamp', y='sunlight', title='Test Input', width=525, height=250)]#  go.Figure(data=go.Scatter(x=[1,2,3,10],y=[1,2,3,4], mode="lines"), layout=go.Layout(title="Invalid", height=150, width=400)) # Fix overall spacing, title spacing, add labels to axes
    return [make_gauge("Temperature", temp_result[0]["value"], "° F", [0, 100], "#dc3545"), make_gauge("Relative Humidity", humidity_result[0]["value"], "%", [0, 100], "#17a2b8"), 
    go.Figure(data=go.Scatter(x=light_result.keys,y=light_result.values, mode="lines"), layout=go.Layout(title="Sunlight", height=250, width=500))]
    #px.line(pd.DataFrame.from_dict(light_result, orient="index"), x="timestamp", y="value", title='Life expectancy in Canada')
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
