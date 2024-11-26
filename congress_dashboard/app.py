import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
import certifi
import ssl
import urllib.request
import wikipediaapi
from dash.dependencies import Input, Output, State
import dash
from dash import dash_table

url = 'https://raw.githubusercontent.com/fivethirtyeight/data/refs/heads/master/congress-demographics/data_aging_congress.csv'

# Create SSL context using certifi
context = ssl.create_default_context(cafile=certifi.where())

# Use urllib to open the URL
with urllib.request.urlopen(url, context=context) as response:
    congress = pd.read_csv(response)
    #print(congress.head(3))  # make sure data was loaded properly
    party_info = pd.read_csv("assets/party_codes.csv")
    #print(party_info.head(3))

# Initialize Wikipedia API with a user agent
user_agent = "MyApp/1.0 (https://myappwebsite.example)"
wiki = wikipediaapi.Wikipedia('en', headers={'User-Agent': user_agent})
list_default = ['Default']


# Helper functions for dropdowns and slider
def create_dropdown_options(series):
    options = [{'label': i, 'value': i} for i in series.sort_values().unique()]
    return options


def create_dropdown_value(series):
    value = series.sort_values().unique().tolist()
    return value


def create_slider_marks(values):
    marks = {i: {'label': str(i)} for i in values}
    return marks


# CHOROPLETH GRAPH
data_c = congress.groupby(by=['state_abbrev', 'congress'])[
    'age_years'].mean().reset_index()
data_c.rename(columns={'age_years': 'average_age'}, inplace=True)
data_c.sort_values(by='congress', inplace=True)
# add more info to Geo map
# dataset: get number of house by different year
temp = congress[congress['chamber'] == 'House'].groupby(
    by=['state_abbrev', 'congress'])['age_years'].size().reset_index()
temp.rename(columns={'age_years': 'number_of_house'}, inplace=True)
# dataset: get number of senate by different year
temp1 = congress[congress['chamber'] == 'Senate'].groupby(
    by=['state_abbrev', 'congress'])['age_years'].size().reset_index()
temp1.rename(columns={'age_years': 'number_of_senate'}, inplace=True)
# merge them then merge to main Geo dataset
temp = temp.merge(temp1, left_on=['state_abbrev', 'congress'],
                  right_on=['state_abbrev', 'congress'])
data_c = data_c.merge(temp, left_on=['state_abbrev', 'congress'],
                      right_on=['state_abbrev', 'congress'])

choropleth = px.choropleth(data_c,
                           locations='state_abbrev',
                           locationmode='USA-states',
                           # Map mode set to US states
                           color='average_age',
                           color_continuous_scale='Reds',
                           scope='usa',
                           range_color=(50, 62),
                           hover_name='state_abbrev',
                           hover_data={'number_of_house': True,
                                       'number_of_senate': True},
                           labels={'state_abbrev': 'State Abbreviations',
                                   'average_age': 'Average Age of Congress Members',
                                   'congress': 'Number of the Congress',
                                   'number_of_house': 'Number of House',
                                   'number_of_senate': 'Number of Senate'},
                           title='Average Age of Congress Members by State',
                           animation_frame='congress'
                           )
choropleth.update_layout(height=750,
                         width=1100)  # adjust for Geomap in Introduction

# graph from Analysis 2
# data2 = congress.groupby(['congress', 'party_code'])['age_years'].mean()
# data2 = data2.reset_index()
# data2.rename(columns={'age_years': 'average_age'}, inplace=True)
#
# # For plot21 # just find out seaborn does not work with dash
# plot21 = px.line(data2, x='congress', y='average_age', color='party_code',
#                  labels={'party_code': 'Party Code',
#                          'average_age': 'Average Age'},
#                  title='bad try: Party-wise Average Age of Congress Members')
#
# party_code_list = [100, 200]
# # For plot22 # just find out seaborn does not work with dash
# plot22 = px.line(data2[data2['party_code'].isin(party_code_list)], x='congress',
#                  y='average_age',
#                  color='party_code',
#                  labels={'party_code': 'Party Code',
#                          'average_age': 'Average Age'},
#                  title='Democrats=100 | Republicans=200\nRepublicans\' average age is lower in recent years')

# HISTOGRAM: Age distribution
histogram = px.histogram(
    congress,
    x='age_years',
    nbins=50,  # Number of bins
    title='Age Years Data is Normally Distributed',
    labels={'age_years': 'Age (Years)'}
)

# STACKED BAR GRAPH

generation_counts = congress.groupby(['congress', 'generation']).size().unstack(
    fill_value=0)
generation_percentages = generation_counts.div(generation_counts.sum(axis=1),
                                               axis=0) * 100
generation_percentages = generation_percentages.reset_index()

# Calculate the average age of each generation per session
avg_age_by_gen = congress.groupby(['congress', 'generation'])[
    'age_years'].mean().reset_index()
avg_age_by_gen = avg_age_by_gen.rename(columns={'age_years': 'average_age'})

# Define generation columns, I was getting weird columns in plot so this filters out the unwanted columns
generation_columns = [col for col in generation_percentages.columns if
                      col not in ['congress', 'level_0', 'index']]

# reshape into correct format for a stacked bar chart
generation_percentages_melted = generation_percentages.melt(id_vars='congress',
                                                            value_vars=generation_columns,
                                                            var_name='generation',
                                                            value_name='percentage')

# Merge with the average age data
merged_data = pd.merge(generation_percentages_melted, avg_age_by_gen,
                       on=['congress', 'generation'])

# Create stacked bar chart using plotly chart with average age in hover over data
stacked_bar = px.bar(merged_data,
                     x='congress',
                     y='percentage',
                     color='generation',
                     title='Generational Makeup of Congress Over Time with Average Age',
                     labels={'percentage': 'Percentage of Congress Members',
                             'congress': 'Congress Session'},
                     hover_name='generation',
                     hover_data={'congress': True, 'percentage': ':.2f',
                                 'generation': True, 'average_age': ':.2f'},
                     color_discrete_sequence=px.colors.qualitative.T10)

# Only display every 5 congress sessions as tick labels for readability
# used chatgpt to figure out bar gap
stacked_bar.update_layout(
    xaxis=dict(title='Congress Session', tickangle=45, tickmode='array',
               tickvals=generation_percentages['congress'][::5]),
    yaxis_title='Percentage of Congress Members',
    legend_title='Generation',
    bargap=0.1,  # Adds a slight gap between bars
)

app = Dash(__name__)

app.layout = html.Div([
    html.Div([  # Left pane
        html.Div([
            html.Div([
                html.H1("Is Congress Getting Older?",
                        style={'marginLeft': '10px', 'color': '#FFFFFF'}),
                html.P("Exploring the age trends of US Congress Members",
                       style={'marginLeft': '10px', 'color': '#FFFFFF'}),
                html.Img(
                    src="assets/congress_seal.png",
                    style={'display': 'block',
                           'marginLeft': 'auto',
                           'marginRight': 'auto',
                           'width': 'auto'}
                ),
            ], style={'height': '550px'}),
            html.Div(style={'height': '300px'}),
            html.Div(style={'height': '750px'}),
            html.Div(style={'height': '1200px'}),
            html.Img(
                src="assets/generations.png",
                style={'display': 'block',
                       'marginLeft': 'auto',
                       'marginRight': 'auto',
                       'width': 'auto'}
            )
        ]),
    ], id='left-container'),

    html.Div([  # Right pane
        html.Div([  # Introduction part
            html.Div(style={'height': '25px'}),
            html.Img(src="assets/intro.png",
                     style={'width': '100%', 'height': '550', 'margin': '0',
                            'padding': '0'}),
            html.Img(src="assets/questions.png",
                     style={'width': '100%', 'height': '300', 'margin': '0',
                            'padding': '0'}),
            html.Div([
                dcc.Graph(id="choropleth", figure=choropleth)
            ])
        ]),
        #
        # html.Div([  # Preview dataset part
        #     html.Div("Preview Dataset:",
        #              style={'fontSize': '30px', 'fontWeight': 'bold', 'marginTop': '5px', 'marginBottom': '5px'}),
        #     html.Div([
        #         dcc.Graph(figure=histogram, style={'width': '70%', 'marginLeft': '0'})
        #     ], style={'padding': '20px'}),
        #     html.Div([
        #         dcc.Graph(figure=plot21, style={'display': 'inline-block', 'width': '50%'}),
        #         dcc.Graph(figure=plot22, style={'display': 'inline-block', 'width': '50%'})
        #     ], style={'padding': '20px'})
        # ]),
        html.Div([  # Average Age of Congress Members
            html.Div([
                html.Div("Average Age of Congress Members Over Time:",
                         style={'fontSize': '30px', 'fontWeight': 'bold',
                                'color'
                                : '#FFFFFF', 'marginTop': '25px',
                                'marginBottom': '20px'}),
                html.Div([
                    html.Div([
                        dcc.Graph(id='line-chart-average-age-party'),
                        html.Div([
                            html.Label("Party", className="dropdown-label"),
                            dcc.Dropdown(
                                id='party-dropdown-average-age',
                                options=[
                                    {'label': 'Democrat', 'value': 'Democrat'},
                                    {'label': 'Republican',
                                     'value': 'Republican'},
                                    {'label': 'Combined', 'value': 'Combined'}
                                ],
                                value=['Combined'],  # Default to combined
                                multi=True  # Allow multiple selections
                            )
                        ], style={'width': '45%', 'display': 'inline-block',
                                  'padding': '10px'}),
                    ], style={'width': '45%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Graph(id='line-chart-average-age-chamber'),
                        html.Div([
                            html.Label("Chamber", className="dropdown-label"),
                            dcc.Dropdown(
                                id='chamber-dropdown-average-age',
                                options=[
                                    {'label': 'Senate', 'value': 'Senate'},
                                    {'label': 'House', 'value': 'House'},
                                    {'label': 'Combined', 'value': 'Combined'}
                                ],
                                value=['Combined'],  # Default to combined
                                multi=True  # Allow multiple selections
                            )
                        ], style={'width': '45%', 'display': 'inline-block',
                                  'padding': '10px'}),
                    ], style={'width': '45%', 'display': 'inline-block'})
                ],style={'marginBottom': '30px'}),

                html.Div([  # Average Age of New vs Returning Members
                    html.Div("Average Age of New vs Returning Members Over Time:",
                             style={'fontSize': '30px', 'fontWeight': 'bold',
                                    'color'
                                    : '#FFFFFF', 'marginTop': '20px',
                                    'marginBottom': '20px'}),
                    html.Div([
                        html.Div([
                            dcc.Graph(id='line-chart-new-vs-returning-party'),
                            html.Div([
                                html.Label("Party", className="dropdown-label"),
                                dcc.Dropdown(
                                    id='party-dropdown-new-vs-returning',
                                    options=[
                                        {'label': 'Democrat', 'value': 'Democrat'},
                                        {'label': 'Republican',
                                         'value': 'Republican'},
                                        {'label': 'Combined', 'value': 'Combined'}
                                    ],
                                    value=['Combined'],  # Default to combined
                                    multi=True  # Allow multiple selections
                                )
                            ], style={'width': '45%', 'display': 'inline-block',
                                      'padding': '10px'}),
                        ], style={'width': '45%', 'display': 'inline-block'}),
                        html.Div([
                            dcc.Graph(id='line-chart-new-vs-returning-chamber'),
                            html.Div([
                                html.Label("Chamber", className="dropdown-label"),
                                dcc.Dropdown(
                                    id='chamber-dropdown-new-vs-returning',
                                    options=[
                                        {'label': 'Senate', 'value': 'Senate'},
                                        {'label': 'House', 'value': 'House'},
                                        {'label': 'Combined', 'value': 'Combined'}
                                    ],
                                    value=['Combined'],  # Default to combined
                                    multi=True  # Allow multiple selections
                                )
                            ], style={'width': '45%', 'display': 'inline-block',
                                      'padding': '10px'}),
                        ], style={'width': '45%', 'display': 'inline-block'})
                    ])
                ])
            ])
        ], style={'height': '1200px', 'width': '1100px'}),

        html.Div([  # Stacked Bar Chart
            html.Div([
                dcc.Graph(id="stacked-bar", figure=stacked_bar)
            ])
        ], style={'marginBottom': '30px'}),

        html.Div("Dataset explore on Wikipedia:",
                 style={'fontSize': '30px', 'fontWeight': 'bold',
                        'marginTop': '5px', 'marginBottom': '5px'}),
        html.Div([  # Congress and Chamber selection
            html.Div([
                html.Label('Congress:'),
                dcc.Dropdown(
                    id='select-congress',
                    options=[{'label': val, 'value': val} for val in
                             list_default + sorted(
                                 congress['congress'].unique().tolist())],
                    value='Default'
                )
            ], style={'width': '25%', 'display': 'inline-block',
                      'paddingRight': '5%'}),
            html.Div([
                html.Label('Chamber:'),
                dcc.Dropdown(
                    id='select-chamber',
                    options=[{'label': val, 'value': val} for val in
                             list_default + sorted(
                                 congress['chamber'].unique().tolist())],
                    value='Default'
                )
            ], style={'width': '25%', 'display': 'inline-block'}),
        ]),

        html.Div([  # State and Party selection
            html.Div([
                html.Label('State:'),
                dcc.Dropdown(
                    id='select-state',
                    options=[{'label': val, 'value': val} for val in
                             list_default + sorted(
                                 congress['state_abbrev'].unique().tolist())],
                    value='Default'
                )
            ], style={'width': '25%', 'display': 'inline-block',
                      'paddingRight': '5%'}),
            html.Div([
                html.Div(id='party-name'),
                dcc.Dropdown(
                    id='select-party',
                    options=[{'label': val, 'value': val} for val in
                             list_default + sorted(
                                 congress['party_code'].unique().tolist())],
                    value='Default'
                )
            ], style={'width': '25%', 'display': 'inline-block'}),
        ]),

        html.Div([  # Slider for Age Range
            html.Label('Age Range:'),
            dcc.RangeSlider(
                id='age-slider',
                min=20,
                max=100,
                value=[20, 100],
                marks={i: str(i) for i in range(20, 101, 10)}
            )
        ], style={'width': '50%', 'marginTop': '20px'}),

        html.Div([  # Filtered Table and Wikipedia Search
            html.Div([
                html.H3('Data After Filter'),
                dash_table.DataTable(
                    id='filtered-table',
                    columns=[{"name": i, "id": i} for i in congress.columns],
                    page_size=10,
                    row_selectable='single'
                )
            ], style={'width': '70%', 'display': 'inline-block'}),
            html.Div([
                html.H3('Selected Bioname:'),
                html.Div(id='selected-bioname'),
                html.Button('Search Wikipedia', id='search-wikipedia',
                            n_clicks=0)
            ], style={'padding-top': '20px', 'backgroundColor': '#e6e3e3'}),
            html.Div(id='wikipedia-summary-table', style={'padding-top': '20px',
                                                          'backgroundColor':
                                                              '#e6e4e4'})
        ])
    ], id='right-container')
], id='container')


@app.callback(
    Output('line-chart-average-age-party', 'figure'),
    Input('party-dropdown-average-age', 'value')
)
def update_average_age_party_chart(selected_parties):
    # Base filtered data containing only valid parties (100 for Democrat, 200 for Republican)
    data = congress[congress['party_code'].isin([100, 200])].copy()

    if 'Combined' in selected_parties and len(selected_parties) == 1:
        # Calculate the combined average if "Combined" is the only selection
        combined_data = (
            data.groupby('congress')['age_years']
            .mean()
            .reset_index()
        )
        combined_data['party_code'] = 'Combined'

        # Prepare the plot data
        fig = px.line(
            combined_data,
            x='congress',
            y='age_years',
            color='party_code',
            title='Average Age by Party (Combined)',
            labels={
                'congress': 'Congress Session',
                'age_years': 'Average Age',
                'party_code': 'Party'
            }
        )
    else:
        # Map selected parties to their codes
        party_map = {'Democrat': 100, 'Republican': 200}
        selected_codes = [party_map[party] for party in selected_parties if
                          party in party_map]

        # Filter for selected parties
        filtered_data = data[data['party_code'].isin(selected_codes)]

        # Prepare the data for plotting
        avg_age_data = (
            filtered_data.groupby(['congress', 'party_code'])['age_years']
            .mean()
            .reset_index()
        )

        # Plot the chart with separate lines for each selected party
        fig = px.line(
            avg_age_data,
            x='congress',
            y='age_years',
            color='party_code',
            title='Average Age by Party',
            labels={
                'congress': 'Congress Session',
                'age_years': 'Average Age',
                'party_code': 'Party'
            }
        )

    fig.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#e6e4e4',  # Background around the plot
        xaxis=dict(
            gridcolor='#8CA8CD',  # Light gray for X-axis grid lines
            title='Congress Session'
        ),
        yaxis=dict(
            gridcolor='#8CA8CD',  # Light gray for Y-axis grid lines
            title='Average Age'
        )
    )

    return fig


@app.callback(
    Output('line-chart-average-age-chamber', 'figure'),
    Input('chamber-dropdown-average-age', 'value')
)
def update_average_age_chamber_chart(selected_chambers):
    # Base filtered data containing only valid chambers (House and Senate)
    data = congress[congress['chamber'].isin(['House', 'Senate'])].copy()

    if 'Combined' in selected_chambers and len(selected_chambers) == 1:
        # Calculate the combined average if "Combined" is the only selection
        combined_data = (
            data.groupby('congress')['age_years']
            .mean()
            .reset_index()
        )
        combined_data['chamber'] = 'Combined'

        # Prepare the plot data
        fig = px.line(
            combined_data,
            x='congress',
            y='age_years',
            color='chamber',
            title='Average Age by Chamber (Combined)',
            labels={
                'congress': 'Congress Session',
                'age_years': 'Average Age',
                'chamber': 'Chamber'
            }
        )
    else:
        # Filter for selected chambers
        filtered_data = data[data['chamber'].isin(selected_chambers)]

        # Prepare the data for plotting
        avg_age_data = (
            filtered_data.groupby(['congress', 'chamber'])['age_years']
            .mean()
            .reset_index()
        )

        # Plot the chart with separate lines for each selected chamber
        fig = px.line(
            avg_age_data,
            x='congress',
            y='age_years',
            color='chamber',
            title='Average Age by Chamber',
            labels={
                'congress': 'Congress Session',
                'age_years': 'Average Age',
                'chamber': 'Chamber'
            }
        )

    return fig


# Classify each member as 'New' if cmltv_cong == 1, otherwise 'Returning'
congress['member_type'] = congress['cmltv_cong'].apply(
    lambda x: 'New' if x == 1 else 'Returning')
# Calculate the average age for new vs. returning members per session
avg_age_by_member_type = congress.groupby(['congress', 'member_type'])[
    'age_years'].mean().reset_index()


@app.callback(
    Output('line-chart-new-vs-returning-party', 'figure'),
    Input('party-dropdown-new-vs-returning', 'value')
)
def update_new_vs_returning_party_chart(selected_parties):
    # Base filtered data containing only valid parties (100 for Democrat, 200 for Republican)
    data = congress[congress['party_code'].isin([100, 200])].copy()

    if 'Combined' in selected_parties and len(selected_parties) == 1:
        # Calculate the combined average if "Combined" is the only selection
        combined_data = (
            data.groupby(['congress', 'member_type'])['age_years']
            .mean()
            .reset_index()
        )
        combined_data['party_member_type'] = combined_data['member_type']

        # Define color mapping for combined
        color_discrete_map = {
            'New': '#87CEEB',  # Light Blue
            'Returning': '#4682B4'  # Dark Blue
        }

        # Prepare the plot data
        fig = px.line(
            combined_data,
            x='congress',
            y='age_years',
            color='party_member_type',
            title='New vs Returning Members (Combined)',
            labels={
                'congress': 'Congress Session',
                'age_years': 'Average Age',
                'party_member_type': 'Member Type'
            },
            color_discrete_map=color_discrete_map
        )
    else:
        # Map selected parties to their codes
        party_map = {'Democrat': 100, 'Republican': 200}
        selected_codes = [party_map[party] for party in selected_parties if
                          party in party_map]

        # Filter for selected parties
        filtered_data = data[data['party_code'].isin(selected_codes)]

        # Prepare the data for plotting
        avg_age_data = (
            filtered_data.groupby(['congress', 'member_type', 'party_code'])[
                'age_years']
            .mean()
            .reset_index()
        )

        # Create a combined column for legend
        avg_age_data['party_member_type'] = avg_age_data.apply(
            lambda
                row: f"{'Democrat' if row['party_code'] == 100 else 'Republican'} ({row['member_type']})",
            axis=1
        )

        # Define color mapping
        color_discrete_map = {
            'Democrat (New)': '#87CEEB',  # Light Blue
            'Democrat (Returning)': '#4682B4',  # Dark Blue
            'Republican (New)': '#FFA07A',  # Light Red
            'Republican (Returning)': '#B22222'  # Dark Red
        }

        # Plot the chart
        fig = px.line(
            avg_age_data,
            x='congress',
            y='age_years',
            color='party_member_type',
            title='New vs Returning Members by Party',
            labels={
                'congress': 'Congress Session',
                'age_years': 'Average Age',
                'party_member_type': 'Party/Member Type'
            },
            color_discrete_map=color_discrete_map
        )

    return fig


@app.callback(
    Output('line-chart-new-vs-returning-chamber', 'figure'),
    Input('chamber-dropdown-new-vs-returning', 'value')
)
def update_new_vs_returning_chamber_chart(selected_chambers):
    # Base filtered data containing only valid chambers
    data = congress[congress['chamber'].isin(['House', 'Senate'])].copy()

    if 'Combined' in selected_chambers and len(selected_chambers) == 1:
        # Calculate the combined average if "Combined" is the only selection
        combined_data = (
            data.groupby(['congress', 'member_type'])['age_years']
            .mean()
            .reset_index()
        )
        combined_data['chamber_member_type'] = combined_data['member_type']

        # Define color mapping for combined
        color_discrete_map = {
            'New': '#87CEEB',  # Light Blue
            'Returning': '#4682B4'  # Dark Blue
        }

        # Prepare the plot data
        fig = px.line(
            combined_data,
            x='congress',
            y='age_years',
            color='chamber_member_type',
            title='New vs Returning Members by Chamber (Combined)',
            labels={
                'congress': 'Congress Session',
                'age_years': 'Average Age',
                'chamber_member_type': 'Member Type'
            },
            color_discrete_map=color_discrete_map
        )
    else:
        # Filter for selected chambers
        filtered_data = data[data['chamber'].isin(selected_chambers)]

        # Prepare the data for plotting
        avg_age_data = (
            filtered_data.groupby(['congress', 'member_type', 'chamber'])[
                'age_years']
            .mean()
            .reset_index()
        )

        # Create a combined column for legend
        avg_age_data['chamber_member_type'] = avg_age_data.apply(
            lambda row: f"{row['chamber']} ({row['member_type']})", axis=1
        )

        # Define color mapping
        color_discrete_map = {
            'House (New)': '#87CEEB',  # Light Blue
            'House (Returning)': '#4682B4',  # Dark Blue
            'Senate (New)': '#FFA07A',  # Light Red
            'Senate (Returning)': '#B22222'  # Dark Red
        }

        # Plot the chart
        fig = px.line(
            avg_age_data,
            x='congress',
            y='age_years',
            color='chamber_member_type',
            title='New vs Returning Members by Chamber',
            labels={
                'congress': 'Congress Session',
                'age_years': 'Average Age',
                'chamber_member_type': 'Chamber/Member Type'
            },
            color_discrete_map=color_discrete_map
        )

    fig.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#e6e4e4',  # Background around the plot
        xaxis=dict(
            gridcolor='#8CA8CD',  # Light gray for X-axis grid lines
            title='Congress Session'
        ),
        yaxis=dict(
            gridcolor='#8CA8CD',  # Light gray for Y-axis grid lines
            title='Average Age'
        )
    )

    return fig


# try to add another section for table
# modify to use party_info dataframe, upon select the party code in the filter to show party name
@app.callback(
    Output('party-name', 'children'),
    Input('select-party', 'value')
)
def update_party_name(select_party):
    if select_party != 'Default':
        party_name = party_info.loc[
            party_info['Party Code'] == int(select_party), 'Party Name'].values
        if len(party_name) > 0:
            return f'Party Code: {party_name[0]}'
    return 'Party Code:'


@app.callback(
    Output('filtered-table', 'data'),
    Input('select-congress', 'value'),
    Input('select-chamber', 'value'),
    Input('select-state', 'value'),
    Input('select-party', 'value'),
    Input('age-slider', 'value')
)
def update_filtered_data(arg_congress, arg_chamber, arg_state, arg_party,
                         arg_age):
    res = congress.copy()
    if arg_congress != 'Default':
        res = res[res['congress'] == arg_congress]
    if arg_chamber != 'Default':
        res = res[res['chamber'] == arg_chamber]
    if arg_state != 'Default':
        res = res[res['state_abbrev'] == arg_state]
    if arg_party != 'Default':
        res = res[res['party_code'] == arg_party]
    res = res[
        (res['age_years'] >= arg_age[0]) & (res['age_years'] <= arg_age[1])]
    return res.to_dict('records')


@app.callback(
    Output('selected-bioname', 'children'),
    Input('filtered-table', 'selected_rows'),
    State('filtered-table', 'data')
)
def update_selected_bioname(selected_rows, table_data):
    if selected_rows is not None and len(selected_rows) > 0:
        selected_row_idx = selected_rows[0]
        selected_name = table_data[selected_row_idx]['bioname']
        return f'Selected Bioname: {selected_name}'
    return 'Click a row to display bioname here.'


@app.callback(
    Output('wikipedia-summary-table', 'children'),
    Input('search-wikipedia', 'n_clicks'),
    State('selected-bioname', 'children')
)
# wiki documentation https://pypi.org/project/Wikipedia-API/?form=MG0AV3
def search_wikipedia(n_clicks, selected_name):
    if selected_name == 'Click a row to display bioname here.':
        return 'Please select who you want to know.'
    if n_clicks > 0 and selected_name:
        user_agent = "MyApp/1.0 (https://myappwebsite.example)"
        wiki = wikipediaapi.Wikipedia('en', headers={'User-Agent': user_agent})

        # Extract the name without "Selected Bioname:"
        name = selected_name.replace('Selected Bioname: ', '').strip()
        parts = name.split(', ')
        parts = parts[::-1]
        parts[1] = parts[1].capitalize()
        name = " ".join(parts)
        res = ['### Wikipedia Summary:', 'name']

        if name:
            page = wiki.page(name)
            if page.exists():
                res.append(page.summary[:500])
                link = f"[Read more on Wikipedia](https://en.wikipedia.org/wiki/{name.replace(' ', '_')})"
                return f'{res[0]}\n\n{res[1]}\n\n{res[2]}\n\n{link}'
            else:
                return f'{res[0]}\n\n{res[1]}\n\nNo page found for this name.'
    return ''


if __name__ == '__main__':
    app.run_server(debug=True)
