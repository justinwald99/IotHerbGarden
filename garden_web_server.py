"""Entry point for the garden web server."""
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import paho.mqtt.client as mqtt
from dash.dependencies import Input, Output

from app import app
from apps import configuration, controls, history, overview
from utils.common import get_broker_ip

# MQTT client
client = mqtt.Client("garden_web_server")
broker_ip = ""

# Global status vars
monitor_online = False
manager_online = False

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
    dcc.Interval(
        id="app_interval",
        interval=5*1000,  # in milliseconds
        n_intervals=0
    ),
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label("Manager:", className="px-2"),
                dbc.Badge("offline", color="danger",
                          pill=True, className="px-2", id="manager_status_pill")
            ]),
            dbc.Col([
                dbc.Label("Monitor:", className="px-2"),
                dbc.Badge("offline", color="danger",
                          pill=True, className="px-2", id="monitor_status_pill")
            ])
        ])
    ], className="container"),
    html.Div(id='page-content', className="container")
])


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


@app.callback(Output("manager_status_pill", "children"),
              Output("manager_status_pill", "color"),
              Output("monitor_status_pill", "children"),
              Output("monitor_status_pill", "color"),
              Input("app_interval", "n_intervals"))
def update_status(n_intervals):
    """Update the status of the manager and monitor scripts."""
    manager_status_text = "online" if manager_online else "offline"
    manager_status_pill = "success" if manager_online else "danger"
    monitor_status_text = "online" if monitor_online else "offline"
    monitor_status_pill = "success" if monitor_online else "danger"
    return manager_status_text, manager_status_pill, monitor_status_text, monitor_status_pill


def mqtt_record_status(client, userdata, msg):
    """Write script status' to global vars to be updated in the UI later."""
    global manager_online
    global monitor_online

    if (msg.topic.split("/")[-1] == "garden_manager"):
        manager_online = msg.payload.decode() == "online"

    if (msg.topic.split("/")[-1] == "garden_monitor"):
        monitor_online = msg.payload.decode() == "online"


if __name__ == '__main__':
    broker_ip = get_broker_ip(__file__)
    client.connect(broker_ip)
    client.loop_start()
    client.message_callback_add("status/+", mqtt_record_status)
    client.subscribe("status/+", qos=2)

    app.run_server(port=8050, host="0.0.0.0")
