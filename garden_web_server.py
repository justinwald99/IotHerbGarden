import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import sys
from app import app
from apps import configuration, controls, history, overview

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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError(
            "Please execute the program: python3 index.py <MQTT_IP>")
    app.run_server(debug=True, port=8050, host="0.0.0.0")
