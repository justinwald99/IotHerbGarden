import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.SKETCHY], suppress_callback_exceptions=True)
app.title = "IoT Herb Garden"
server = app.server
