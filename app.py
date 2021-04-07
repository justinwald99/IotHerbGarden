import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY])
app.title = "IoT Herb Garden"
server = app.server
