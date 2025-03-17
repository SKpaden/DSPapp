from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# Load data:
df = pd.read_csv("data/cleaned_BFL_data.csv")
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year

grouped_year = df.groupby(by='year').size()

test_fig = px.line(grouped_year,title="Line Plot for Number of Base Fatalities per Year").update_layout(
                                template='plotly_dark',
                                plot_bgcolor='rgba(0, 0, 0, 0)',
                                paper_bgcolor='rgba(0, 0, 0, 0)',
                            )

test_fig2 = px.bar(df.groupby(by='age').size(),title="Bar Plot for Number of Base Fatalities per Age").update_layout(
                                template='plotly_dark',
                                plot_bgcolor='rgba(0, 0, 0, 0)',
                                paper_bgcolor='rgba(0, 0, 0, 0)',
                            )

app = Dash(__name__)
app.layout = html.Div(
    children=[
        html.H1("How Dangerous is Skydiving?", style={"textAlign": "center"}),
        html.P("This is a paragraph with a description."),
        dcc.Input(placeholder="Type something...", style={"marginRight": "10px"}),
        html.Button("Click Me", id="button"),
        dcc.Tabs(id="tabs", value="tab-1", children=[
        dcc.Tab(label="Tab 1: Scatter Plot", value="tab-1", className="custom-tab", selected_className="custom-tab--selected"),
        dcc.Tab(label="Tab 2: Bar Plot", value="tab-2", className="custom-tab", selected_className="custom-tab--selected"),
    ]),
        html.Div(id="tab-content"),  # content of the currently selected tab
        dcc.Graph(figure=test_fig),  # static graph
        # Container for another dropdown and plot:
        html.Div([
            dcc.Dropdown(
                id="dropdown-3",
                options=[
                    {"label": "Per Country", "value": "country"},
                    {"label": "Per Location", "value": "location"},
                    {"label": "Per Age", "value": "age"}
                ],
                value="age",  # default selection
                style={"width": "50%"}
            ),
            #dcc.Graph(figure=test_fig2),
            dcc.Graph(id="graph-3")  # dynamic bar plot

        ])
    ],
    style={"padding": "20px"}
)

# Callback to render content for each tab
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value")
)
def render_tab_content(tab):
    if tab == "tab-1":
        return html.Div([
            html.H3("Dynamic Scatter Plot"),
            dcc.Dropdown(
                id="dropdown-1",
                options=[
                    {"label": "skydives", "value": "skydives"},
                    {"label": "base_jumps", "value": "base_jumps"},
                    {"label": "WS_skydives", "value": "WS_skydives"}
                ],
                value="skydives",  # default selection
                style={"width": "50%"}
            ),
            dcc.Loading(id="loading-1",  # prevent white square when plot hasn't loaded yet
                type="circle",
                children = dcc.Graph(id="graph-1")  # graph for Tab 1
            )
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
                value="skydives",  # default selection
                style={"width": "50%"}
            ),
            dcc.Loading(id="loading-2",
                type="circle",
                children = dcc.Graph(id="graph-2")  # graph for Tab 2
            )
        ])
    

# Callback for the dynamic line plot in Tab 1:
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

# Callback for the dynamic bar plot in Tab 2:
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

# Callback for the dynamic bar plot in Tab 2:
@app.callback(
    Output("graph-3", "figure"),
    Input("dropdown-3", "value")
)
def update_graph_3(selected_column):
    return px.bar(df.groupby(by=selected_column).size().sort_values(ascending=False),height=800, title=f"Bar Plot for Number of Accidents per {selected_column}").update_layout(
                                template='plotly_dark',
                                plot_bgcolor='rgba(0, 0, 0, 0)',
                                paper_bgcolor='rgba(0, 0, 0, 0)'
                            )

if __name__ == "__main__":
    app.run_server(debug=True)  # locally with debug mode enabled
else:
    server = app.server  # server for Render