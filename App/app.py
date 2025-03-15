from dash import Dash, html

app = Dash(__name__)
app.layout = [html.Div(children='Hello World')]
server = app.server  # Expose the server for Render