from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# Load data:
df = pd.read_csv("data/cleaned_BFL_data.csv")
df['date'] = pd.to_datetime(df['date'])

app = Dash(__name__)
app.layout = html.Div(
    children=[
        html.H1("My Enhanced Website", style={"textAlign": "center"}),
        html.P("This is a paragraph with a description."),
        dcc.Input(placeholder="Type something...", style={"marginRight": "10px"}),
        html.Button("Click Me", id="button"),
        dcc.Tabs(id="tabs", value="tab-1", children=[
        dcc.Tab(label="Tab 1: Line Plot", value="tab-1", className="custom-tab", selected_className="custom-tab--selected"),
        dcc.Tab(label="Tab 2: Bar Plot", value="tab-2", className="custom-tab", selected_className="custom-tab--selected"),
    ]),
        html.Div(id="tab-content"),  # Content of the currently selected tab
    
    ],
    style={"padding": "20px"}
)

@app.callback(
    Output("dynamic_graph", "figure"),
    Input("dropdown", "value")
)

# Callback to render content for each tab
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value")
)
def render_tab_content(tab):
    if tab == "tab-1":
        return html.Div([
            html.H3("Dynamic Line Plot"),
            dcc.Dropdown(
                id="dropdown-1",
                options=[
                    {"label": "skydives", "value": "skydives"},
                    {"label": "base_jumps", "value": "base_jumps"},
                    {"label": "WS_skydives", "value": "WS_skydives"}
                ],
                value="skydives",  # Default selection
                style={"width": "50%"}
            ),
            dcc.Graph(id="graph-1")  # Graph for Tab 1
        ])
    elif tab == "tab-2":
        return html.Div([
            html.H3("Dynamic Bar Plot"),
            dcc.Dropdown(
                id="dropdown-2",
                options=[
                    {"label": "skydives", "value": "skydives"},
                    {"label": "base_jumps", "value": "base_jumps"},
                    {"label": "WS_skydives", "value": "WS_skydives"}
                ],
                value="skydives",  # Default selection
                style={"width": "50%"}
            ),
            dcc.Graph(id="graph-2")  # Graph for Tab 2
        ])
    

# Callback for the dynamic line plot in Tab 1
@app.callback(
    Output("graph-1", "figure"),
    Input("dropdown-1", "value")
)
def update_graph_1(selected_column):
    return px.scatter(df, x="date", y=selected_column, title=f"Scatter Plot for {selected_column}").update_layout(
                                template='plotly_dark',
                                plot_bgcolor='rgba(0, 0, 0, 0)',
                                paper_bgcolor='rgba(0, 0, 0, 0)',
                                
                            )

# Callback for the dynamic bar plot in Tab 2
@app.callback(
    Output("graph-2", "figure"),
    Input("dropdown-2", "value")
)
def update_graph_2(selected_column):
    return px.bar(df, x="age", y=selected_column, title=f"Bar Plot for {selected_column}").update_layout(
                                template='plotly_dark',
                                plot_bgcolor='rgba(0, 0, 0, 0)',
                                paper_bgcolor='rgba(0, 0, 0, 0)',
                                
                            )



def update_graph(selected_column):
    return px.scatter(df, x="date", y=selected_column, title=f"Line Chart of {selected_column}").update_layout(
                                template='plotly_dark',
                                plot_bgcolor='rgba(0, 0, 0, 0)',
                                paper_bgcolor='rgba(0, 0, 0, 0)',
                                
                            )

server = app.server