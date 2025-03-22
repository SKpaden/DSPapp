from dash import dash, dcc, html, Input, Output, State, callback_context
import plotly.express as px
import pandas as pd
from scipy.stats import pearsonr
import statsmodels.api as sm

# Load BFL data:
base_df = pd.read_csv("data/cleaned_BFL_data.csv")
# Load USPA data:
uspa_df = pd.read_csv("data/uspa_data_done.csv", delimiter=';', low_memory=False)

# Convert some columns:
base_df['date'] = pd.to_datetime(base_df['date'])
base_df['description'] = base_df['description'].fillna('')

uspa_df['report_date'] = pd.to_datetime(uspa_df['report_date'], errors='coerce')
uspa_df['technical_error_component'] = uspa_df['human_error'].apply(lambda x: x == 'No')

temp_df = base_df.copy(deep=True)  # copy df to not change original df

# Split the comma-separated values into lists:
temp_df["possible_factors"] = temp_df["possible_factors"].str.split(", ")

# Explode the list into individual rows:
df_exploded = temp_df.explode("possible_factors")
factor_list = sorted(df_exploded["possible_factors"].unique())

# Numeric columns for BASE data:
base_numeric_cols = ["skydives", "WS_skydives", "base_jumps", "WS_base_jumps", "base_seasons", "age"]


# Initialize Dash app:
app = dash.Dash(__name__)

############################################
# App Layout
############################################

# Layout:
app.layout = html.Div([
    html.H1("Jumping Data Analysis", style={"textAlign": "center"}),
    
    dcc.Tabs(id="tabs", value="uspa-tab", children=[

        # USPA Data Tab:
        dcc.Tab(label="USPA Data", value="uspa-tab", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.H2("USPA Data Visualizations", style={"margin": "10px"}),
            html.P("Question 6"),
            #dcc.Graph(
            #    figure=px.scatter(title="USPA Data Coming Soon").update_layout(template='plotly_dark',
            #                                                                   plot_bgcolor='rgba(0, 0, 0, 0)',
            #                                                                  paper_bgcolor='rgba(0, 0, 0, 0)',)
            #)

            dcc.Dropdown(
                id="uspa-chart-dropdown",
                options=[{"label": "Pie Chart", "value": "pc"},
                         {"label": "Bar Chart", "value": "bc"},
                         {"label": "Line Chart", "value": "lc"}],
                value="bc",
                multi=False,
                style={"width": "50%", "margin": "10px"}
            ),

            dcc.Dropdown(
                id="uspa-bar-dropdown",
                options=[{"label": "by fatal or not", "value": "fatal"},
                         {"label": "by category", "value": "category"}],
                value="category",
                multi=False,
                style={"width": "50%", "margin": "10px", "display": "block"}
            ),
            dcc.Graph(id="uspa-bar-plot")
        ]),

        ############################################
        # Second Tab: BFL Data
        ############################################

        # BASE Fatalities Tab:
        dcc.Tab(label="BASE Fatalities", value="base-tab", className="custom-tab", selected_className="custom-tab--selected", children=[
            html.H2("BASE Fatality Visualizations", style={"margin": "10px"}),
            
            # Histogram Section:
            html.H3("Histogram", style={"textAllign": "center"}),
            dcc.Dropdown(
                id="base-hist-dropdown",
                options=[{"label": col, "value": col} for col in base_numeric_cols],
                value="base_jumps",
                multi=False,
                style={"width": "50%", "margin": "10px"}
            ),
            dcc.Graph(id="base-hist-plot"),

            # Results:
            html.P("All the numeric data is right-skewed (median < mean). "
            "This may imply that BASE fatalities occur more often with inexperienced jumpers. "
            "However, this is based only on the fatality numbers, successful jumps are not accounted for!"),

            html.Hr(),
            
            # Scatter Section:
            html.H3("Scatter with Regression"),
            dcc.Checklist(
                id="base-scatter-checklist",
                options=[{"label": col, "value": col} for col in base_numeric_cols],
                value=["base_jumps", "base_seasons"],
                inline=True,
                style={"margin": "20px"}
            ),
            dcc.Graph(id="base-scatter-plot"),

            html.Hr(),

            # Word Cloud Section:

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

            # Victim's name:
            html.H3(id="BFL-victim-name", style={"fontSize": "18px",
                                            "padding": "20px",
                                            "textAlign": "center"
                                            }),


            # Paragraph for incident description:
            html.Div(id="description", style={"height": "200px",
                                              "overflow-y": "scroll",
                                              "border": "1px solid black",
                                              "padding": "10px",
                                              "margin": "10px",
                                              "whiteSpace": "pre-wrap"}  # convert \n to actual line break
            ),

            # Buttons to get next and previous incident description/report:
            html.Button("Previous", id="prev-button", disabled=True),  # initially disabled
            html.Button("Next", id="next-button"),

            # Hidden component to store the current index:
            dcc.Store(id="current-index", data=0)
        ])
        
    ])
])

############################################
# Callbacks for BFL
############################################

# Callback for BASE Histogram:
@app.callback(
    Output("base-hist-plot", "figure"),
    Input("base-hist-dropdown", "value")
)
def update_base_histogram(selected_col):
    data = base_df[selected_col].dropna()
    mean_val = data.mean()
    median_val = data.median()
    
    fig = px.histogram(
        data_frame=pd.DataFrame({selected_col: data}),
        x=selected_col,
        nbins=30,
        title=f"Histogram of {selected_col} (n={len(data)})",
        labels={selected_col: selected_col}
    )
    
    fig.add_vline(x=mean_val, line_dash="dash", line_color="red", annotation_text=f"Mean={mean_val:.1f}")
    fig.add_vline(x=median_val, line_dash="dash", line_color="green", annotation_text=f"Median={median_val:.1f}")
    
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        bargap=0.1,
        showlegend=False,
        annotations=[
            dict(x=mean_val, y=0.9, xref="x", yref="paper", text=f"Mean={mean_val:.1f}", showarrow=False),
            dict(x=median_val, y=0.8, xref="x", yref="paper", text=f"Median={median_val:.1f}", showarrow=False)
        ]
    )
    
    return fig

# Callback for BASE Scatter Plot:
@app.callback(
    Output("base-scatter-plot", "figure"),
    Input("base-scatter-checklist", "value")
)
def update_base_scatter(selected_cols):
    if len(selected_cols) != 2:  # more or less than 2 ticked
        fig = px.scatter(title="Please select exactly 2 attributes")
        fig.update_layout(template='plotly_dark',
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)',)
        return fig
    
    x_col, y_col = selected_cols
    df_clean = base_df[[x_col, y_col]].dropna()  # necessary for p-value and correlation
    n_rows = df_clean.shape[0]
    
    if n_rows < 10:  # not enough data
        return px.scatter(title=f"No data available for {x_col} vs. {y_col}")
    
    
    corr, p_value = pearsonr(df_clean[x_col], df_clean[y_col])
    X = sm.add_constant(df_clean[x_col])
    model = sm.OLS(df_clean[y_col], X).fit()
    slope = model.params.iloc[1]
    std_err = model.bse.iloc[1]
    conf_int = model.conf_int().loc[x_col].values
    
    fig = px.scatter(
        df_clean,
        x=x_col,
        y=y_col,
        title=f"{x_col} vs. {y_col}",
        trendline="ols",
        trendline_color_override="red"
    )

    fig.update_layout(template='plotly_dark',
                      plot_bgcolor='rgba(0, 0, 0, 0)',
                      paper_bgcolor='rgba(0, 0, 0, 0)')
    
    stats_text = (f"n={n_rows}/535,\n"
                  f"Corr={corr:.3f}, P={p_value:.3f},\n"
                  f"Slope={slope:.3f}, SE={std_err:.3f},\n"
                  f"95% CI=[{conf_int[0]:.3f}, {conf_int[1]:.3f}]")
    
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.45, y=1.10,
        text=stats_text,
        showarrow=False,
        bgcolor="rgba(0, 0, 0, 0)",
        bordercolor="rgba(0, 0, 0, 0)",
        borderwidth=1
    )
    
    return fig

# Combined callback for BFL incident reports and names:
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

    # Navigate with buttons:
    elif triggered_id == "prev-button" and current_index > 0:
        current_index -= 1
    elif triggered_id == "next-button" and current_index < len(data) - 1:
        current_index += 1
    
    # Get the current description:
    description = data.iloc[current_index]['description'] if not data.empty else "No incidents available."
    if description == "":
            description = "No description available for this incident."

    name = "In Memory of "
    name += data.iloc[current_index]['name']
    
    # Enable/disable buttons based on boundaries:
    prev_disabled = current_index == 0
    next_disabled = current_index == len(data) - 1

    return current_index, prev_disabled, next_disabled, description, name

############################################
# Callbacks for USPA
############################################
# Callback for USPA Bar Plot:
@app.callback(
    [Output("uspa-bar-plot", "figure"),
     Output(component_id='uspa-bar-dropdown', component_property='style')],
    [Input("uspa-bar-dropdown", "value"),
     Input("uspa-chart-dropdown", "value")]
)
def update_uspa_bar(selected_col, selected_chart):
    if selected_chart == "bc":  # bar chart
        visible = {"width": "50%", "margin": "10px", 'display': 'block'}
        category_counts = uspa_df.groupby([selected_col, 'technical_error_component']).size().reset_index(name='Count')
        fig = px.bar(
        category_counts, 
        x='Count', 
        y=selected_col, 
        color='technical_error_component', 
        title=f'Skydiving Accidents by {selected_col}',
        labels={'technical_error_component': 'Technical Error Involved', selected_col: 'Accident Category'},
        barmode='stack',
        orientation='h'
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        
    elif selected_chart == "lc":  # line chart
        visible = {'display': 'none'}
        df_time_series = uspa_df.groupby(['report_date', 'technical_error_component']).size().reset_index(name='Count')

        fig = px.line(
            df_time_series, 
            x='report_date', 
            y='Count', 
            color='technical_error_component', 
            title='Trend of Skydiving Accidents Over Time',
            labels={'technical_error_component': 'Technical Error Involved', 'report_date': 'Date', 'Count': 'Number of Accidents'},
            markers=True
        )
    
    elif selected_chart == "pc":  # pie chart
        # Count occurrences of technical vs non-technical errors:
        technical_error_counts = uspa_df['technical_error_component'].value_counts().reset_index()
        technical_error_counts.columns = ['Technical Error Contribution', 'Count']
        technical_error_counts['Technical Error Contribution'] = technical_error_counts['Technical Error Contribution'].map({True: 'Yes', False: 'No'})
        visible = {'display': 'none'}
        fig = px.pie(
            technical_error_counts, 
            names='Technical Error Contribution', 
            values='Count', 
            title='Skydiving Accidents: Technical Error Contribution',
            hole=0.4,
            color='Technical Error Contribution',
            color_discrete_map={'Yes': 'red', 'No': 'blue'}
        )
        fig.update_traces(textinfo='percent+label')

    fig.update_layout(template='plotly_dark',
                      plot_bgcolor='rgba(0, 0, 0, 0)',
                      paper_bgcolor='rgba(0, 0, 0, 0)')
    
    return fig, visible

############################################
# Run app
############################################

# Run the app:
if __name__ == "__main__":
    app.run_server(debug=True)  # locally with debug mode enabled
else:
    server = app.server  # server for Render