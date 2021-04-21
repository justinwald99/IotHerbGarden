import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import sys
from app import app
from apps import configuration, controls, history, overview
from utils.db_interaction import create_plant
from sqlalchemy import create_engine, text, Table, desc, select
from sqlalchemy.sql.schema import MetaData

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Overview", href="/")),
        dbc.NavItem(dbc.NavLink("History", href="history")),
        dbc.NavItem(dbc.NavLink("Controls", href="controls")),
        dbc.NavItem(dbc.NavLink("Configuration", href="configuration")),
    ],
    brand=app.title,
    brand_href="/",
    color="primary",
    dark=True
)

app.layout = html.Div([
    navbar,
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', className="container")
]
)


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return overview.layout
    elif pathname == '/history':
        return history.layout
    elif pathname == '/controls':
        return controls.layout
    elif pathname == '/configuration':
        return configuration.layout
    else:
        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognized..."),
            ]
        )


def check_plants():
    engine = create_engine("sqlite+pysqlite:///garden.db", future=True)
    metadata = MetaData()
    plant_table = Table("plant", metadata, autoload_with=engine)
    sensor_table = Table("sensor", metadata, autoload_with=engine)
    with engine.connect() as conn:
        plants = conn.execute(
            select(plant_table.c.id)
        ).fetchall()
        humidity_sensors = conn.execute(
            select(sensor_table.c.id).where(sensor_table.c.type == 'soil_humidity')
        ).fetchall()
        # now we have all plants and soil humidity sensors
        diff = len(humidity_sensors) - len(plants)
        if diff > 0:
            for i in reversed(range(diff)):
                create_plant(engine, metadata, {
                    "id":len(humidity_sensors) - i,
                    "name":f"plant_{len(humidity_sensors) - i}",
                    "humidity_sensor_id":humidity_sensors[i][0], #make sure we don't have to index any further into it :) it's possible that you have to add an ["id"] at the end.
                    "pump_id":len(humidity_sensors) - i,                     #maybe we can change this? currently pump_id is always the plant_id.
                    "target":50,
                    "watering_cooldown":300,
                    "watering_duration":1,
                    "humidity_tolerance":5
                }) # id is len(humidity_sensors - i)
            

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError(
            "Please execute the program: python3 index.py <MQTT_IP>")
    check_plants()
    app.run_server(debug=True, port=8050, host="0.0.0.0")
