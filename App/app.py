from dash import Dash, html, dcc, Input, Output, State, callback_context
import pandas as pd
import plotly.express as px


def init_stacked_bar():
    # Find the top 5 most frequent locations:
    top_locations = df['location'].value_counts().nlargest(5).index

    # Replace locations not in the top 5 with "Other":
    df['filtered_location'] = df['location'].apply(lambda x: x if x in top_locations else 'Other')

    # Group data by cause_of_death and filtered_location:
    grouped_data = df.groupby(['cause_of_death', 'filtered_location']).size().reset_index(name='number_of_fatal_accidents')

    # Sort the DataFrame by the total number of fatal accidents:
    sorted_data = grouped_data.groupby('cause_of_death')['number_of_fatal_accidents'].sum().sort_values(ascending=False)

    # Use the sorted order to reindex your DataFrame:
    grouped_data['cause_of_death'] = pd.Categorical(
        grouped_data['cause_of_death'],
        categories=sorted_data.index,
        ordered=True
    )

    # Pivot the data for stacked bar plotting:
    pivot_data = grouped_data.pivot(index='cause_of_death', columns='filtered_location', values='number_of_fatal_accidents')

    return px.bar(pivot_data, title ="Stacked Bar Chart of Causes of Death for Top Countries", height=800).update_layout(
                                template='plotly_dark',
                                plot_bgcolor='rgba(0, 0, 0, 0)',
                                paper_bgcolor='rgba(0, 0, 0, 0)',
                            )

# Load data:
df = pd.read_csv("data/cleaned_BFL_data.csv")
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['description'] = df['description'].fillna('')  # for distinguishing empty descr

# Reduce to only unique values:
factor_list = df['possible_factors'].unique().tolist()
i = 0
while i < len(factor_list):  # while loop, because list size expands dynamically
    factor_list[i:i+1] = factor_list[i].split(', ')  # insert new list into list
    i+=1
factor_list = set(factor_list)  # remove duplicates

temp_df = df.copy(deep=True)  # copy df to not change original df

# Split the comma-separated values into lists:
temp_df["possible_factors"] = temp_df["possible_factors"].str.split(", ")

# Explode the list into individual rows:
df_exploded = temp_df.explode("possible_factors")

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

stacked_bar = init_stacked_bar()

# Layout:
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

        ]),
        dcc.Loading(id="loading-3",
                    type="circle",
                    children=dcc.Graph(figure=stacked_bar)
                    ),

        # Header for word cloud:
        html.H1("What Factors Are Most Prominent in Base Fatalities?", style={"textAlign": "center"}),

        # Wordcloud image:
        html.Div([
            html.Img(src="/assets/wordcloud.png", style={"width": "60%", "height": "auto", "align": "center"})
        ], style={'textAlign': 'center'}
        ),

        # Disclaimer text:
        html.Div(children=[
            html.H2("Disclaimer"),
            html.H3("These are incident descriptions from the Base Fatality List (BFL)."
            " Some contain detailed reports of what happened and led to the accident, some contain emotional words from family or friends."
            " We shall learn from their mistakes to prevent more accidents in the future.")
        ], style={"textAlign": "center", "white-space": "pre-wrap"}
        ),

        # Explanation for dropdown:
        html.H4("Choose a possible factor to browse reports for:", style={"textAlign": "left"}),

        # Factor selector:
        dcc.Dropdown(
            id="factor-dropdown",
            options=[{"label": factor, "value": factor} for factor in factor_list],
            value="Canopy Entanglement",  # default selected value
            style={"width": "50%"},
            className="large-dropdown"  # custom class for styling
        ),

        # Container for victims name:
        html.H3(id="BFL-victim-name", style={"fontSize": "18px",
                                            "padding": "20px",
                                            "textAlign": "center"
                                            }),

        # Paragraph for incident description:
        html.Div(id="description", style={"white-space": "pre-wrap",  # convert \n to actual line break (html)
                                          "fontSize": "18px",
                                          "padding": "20px",
                                          "textAlign": "left"
                                          }),

        # Buttons to get next and previous incident description/report:
        html.Button("Previous", id="prev-button", disabled=True),  # initially disabled
        html.Button("Next", id="next-button"),

        # Hidden component to store the current index:
        dcc.Store(id="current-index", data=0)

    ],
    style={"padding": "20px"}
)

# Combined callback
@app.callback(
    [Output("current-index", "data"),
     Output("prev-button", "disabled"),
     Output("next-button", "disabled"),
     Output("description", "children"),
     Output("BFL-victim-name", "children")],
    [Input("factor-dropdown", "value"),
     Input("prev-button", "n_clicks"),
     Input("next-button", "n_clicks")],
    State("current-index", "data")
)
def reset_index_on_factor_change(selected_factor, prev_clicks, next_clicks, current_index):
    # Reset the index to 0 and update description:
    data = df_exploded.query(f'possible_factors == "{selected_factor}"')
    data = data.query("description != ''")

    # Get the triggered input ("next", "previous" or "dropdown"):
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    #print(callback_context.triggered[0])

    # Reset index to 0 if the dropdown changes:
    if triggered_id == "factor-dropdown":
        current_index = 0

    # Navigate with buttons
    elif triggered_id == "prev-button" and current_index > 0:
        current_index -= 1
    elif triggered_id == "next-button" and current_index < len(data) - 1:
        current_index += 1
    
    # Get the current description
    description = data.iloc[current_index]['description'] if not data.empty else "No incidents available."
    if description == "":  # If it's a Pandas Series
            description = "No description available for this incident."

    name = "In Memory of "
    name += data.iloc[current_index]['name']
    
    # Enable/disable buttons based on boundaries
    prev_disabled = current_index == 0
    next_disabled = current_index == len(data) - 1

    return current_index, prev_disabled, next_disabled, description, name


# Callback to render content for each tab:
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