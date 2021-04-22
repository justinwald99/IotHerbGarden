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

# Setup database interaction
engine = create_engine("sqlite+pysqlite:///garden.db", future=True)
metadata = MetaData()
plant_table = Table("plant", metadata, autoload_with=engine)
sensor_table = Table("sensor", metadata, autoload_with=engine)

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
    """Check that every soil_humidity sensor has a plant associated with it.
    
    If there exists a soil_humidity sensor that does not have a plant associated,
    create a new plant with default values in the DB.
    """
    with engine.connect() as conn:
        plant_ids = conn.execute(
            select(plant_table.c.id)
        ).fetchall()
        # Convert list of tuples into list of ids.
        plant_ids = [id for id, in plant_ids]

        associated_sensor_ids = conn.execute(
            select(plant_table.c.humidity_sensor_id)
        ).fetchall()
        associated_sensor_ids = [id for id, in associated_sensor_ids]

        humidity_sensors = conn.execute(
            select(sensor_table.c.id).where(sensor_table.c.type == 'soil_humidity')
        ).fetchall()
        humidity_sensors = [id for id, in humidity_sensors]

        # now we have all plants and soil humidity sensors
        for humidity_sensor_id in humidity_sensors:
            # Create plants for every humidity sensor
            if humidity_sensor_id  not in associated_sensor_ids:
                # Plant with default values
                create_plant(engine, metadata, {
                    # plant_ids is combined with single-element list to prevent max([])
                    "name": f"plant_{max(plant_ids + [0]) + 1}",
                    "humidity_sensor_id": humidity_sensor_id,
                    "pump_id": max(plant_ids + [0]) + 1,
                    "target": 50,
                    "watering_cooldown": 300,
                    "watering_duration": 1,
                    "humidity_tolerance": 5
                })
                # Recursive call so we don't have to keep track of generated ids
                check_plants()
                return
            

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError(
            "Please execute the program: python3 index.py <MQTT_IP>")

    check_plants()

    app.run_server(debug=True, port=8050, host="0.0.0.0")
