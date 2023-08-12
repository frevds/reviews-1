# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(
            id='site-dropdown', 
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                *[  # expand array to arguments
                    { 'label': f"Only {site}", 'value': site } 
                        for site in spacex_df['Launch Site'].unique() 
                ]
            ], 
            value='ALL', 
            placeholder='Select Launch Site', 
            searchable=True
        ), 
        html.Br(),

        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id='success-pie-chart')),

        html.P("Payload range (kg):"),
        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(
            id='payload-slider', 
            value=[ min_payload, max_payload ], 
            min=0, max=max(10000, max_payload), 
            step=1000
        ), 

        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ]
)

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def make_figure(site):
    if site == 'ALL' or not site: 
        data = spacex_df[spacex_df['class'] == 1].groupby('Launch Site', as_index=False).count()
        fig = px.pie(data, values='class', names='Launch Site', title=f"Total success per site")
    else: 
        data = spacex_df[spacex_df['Launch Site'] == site].groupby('class', sort=True, as_index=False).count()
        fig = px.pie(data, values='Flight Number', names=[ "Failure", "Success" ], title=f"Success rate for site {site}", 
                     color_discrete_sequence=['#DD5555', '#55DD55'])
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'), 
    [
        Input(component_id='site-dropdown', component_property='value'), 
        Input(component_id='payload-slider', component_property='value')
    ]
)
def make_scatter(site, range):
    data = spacex_df.loc[spacex_df['Payload Mass (kg)'].between(range[0], range[1], inclusive='both')]
    if site == 'ALL' or not site: 
        title = "Correlation of Payloads and Success"
    else: 
        data = data.loc[spacex_df['Launch Site'] == site]
        title = f"Correlation of Payloads and Success for site {site}"
    plot = px.scatter(data_frame=data, x='Payload Mass (kg)', y='class', color='Booster Version Category', title=title)
    return plot

# Run the app
if __name__ == '__main__':
    app.run_server()
