from dash import Dash, html, dcc

app = Dash(__name__)
app.layout = html.Div(
    children=[
        html.H1("My Enhanced Website", style={"textAlign": "center", "color": "teal"}),
        html.P("This is a paragraph with a description."),
        dcc.Input(placeholder="Type something...", style={"marginRight": "10px"}),
        html.Button("Click Me", id="button"),
        dcc.Graph(
            id="example-graph",
            figure={
                "data": [{"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar", "name": "Sample"}],
                "layout": {"title": "Example Graph"}
            }
        )
    ],
    style={"padding": "20px"}
)
server = app.server  # Expose the server for Render