# Import required libraries
import pandas as pd
import numpy as np
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': val, 'value': val} for val in np.unique(spacex_df['Launch Site'])],
                                             value='ALL',
                                             placeholder='Select a Launch Site',
                                             searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, 
                                                marks={f'{i}': i for i in np.arange(0, 10001, 1000)},
                                                value=[min_payload, max_payload],
                                                tooltip={"placement": "bottom", "always_visible": True}
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        filtered_df = filtered_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(filtered_df, values='class', 
                     names='Launch Site', 
                     title=f'Total Success Launches by Site')
    else:
        # return the outcomes piechart for a selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        filtered_df = filtered_df['class'].value_counts().reset_index()
        filtered_df.columns = ['values', 'counts']
        fig = px.pie(
            filtered_df, values='counts', 
            names='values', 
            title=f'Total Success Launches for Site: {entered_site}'
        )

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_plot(entered_site, payload_range):
    print(min_payload, max_payload)
    filtered_df = spacex_df
    filtered_df = filtered_df[filtered_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1])]
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    fig = px.scatter(
        filtered_df, x='Payload Mass (kg)', y='class',
        color='Booster Version Category'
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
