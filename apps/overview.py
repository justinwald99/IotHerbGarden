import dash_html_components as html
import dash_core_components as dcc
from utils.ui_elements import make_gauge


layout = [
    html.Div(
        [
            html.H1("Overview", className="card-title"),
            html.Div(
                [
                    html.H2("Ambient", className="card-subtitle"),
                    html.Div(
                        [
                            dcc.Graph(figure=make_gauge("Temperature", 90, "° F", [0, 100], "#dc3545"), className="col-md-3"),
                            dcc.Graph(figure=make_gauge("Relative Humidity", 70, "%", [0, 100], "#17a2b8"), className="col-md-3")
                        ],
                        className="row"
                    )
                    
                ],
                className="card-body"
            )
        ],
        className="container card m-1"
    )

]