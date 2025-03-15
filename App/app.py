from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# Load data:
df = pd.read_csv("data\cleaned_BFL_data.csv")
df['date'] = pd.to_datetime(df['date'])

app = Dash(__name__)
app.layout = html.Div(
    children=[
        html.H1("My Enhanced Website", style={"textAlign": "center"}),
        html.P("This is a paragraph with a description."),
        dcc.Input(placeholder="Type something...", style={"marginRight": "10px"}),
        html.Button("Click Me", id="button"),
        dcc.Dropdown(
            id="dropdown",
            options=[
            {"label": ['skydives', 'base_jumps'], "value": ['skydives', 'base_jumps']}
        ],
        value=df.columns[1]
        )
    ],
    style={"padding": "20px"}
)

@app.callback(
    Output("dynamic-graph", "figure"),
    Input("dropdown", "value")
)
def update_graph(selected_column):
    return px.line(df, x="date", y=selected_column, title=f"Line Chart of {selected_column}")

server = app.server  # Expose the server for Render