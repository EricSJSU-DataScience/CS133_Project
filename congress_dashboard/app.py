from app_instance import app
from dash import Dash, html, dcc
from dash import dash_table
from congress_dashboard.figures import *
from congress_dashboard.callbacks import *


list_default = ['Default']

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
            html.Div(style={'height': '775px'}),
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
                     style={'width': '1100px', 'height': '550px', 'margin': '0',
                            'padding': '0'}),
            html.Img(src="assets/questions.png",
                     style={'width': '1100px', 'height': '300px', 'margin': '0',
                            'padding': '0'}),
            html.Div([
                dcc.Graph(id="choropleth", figure=create_choropleth())
            ], style={'height': '750px', 'width': '1100px'})
        ]),
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
                    ], style={'width': '50%', 'display': 'inline-block'}),
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
                    ], style={'width': '50%', 'display': 'inline-block'})
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
                        ], style={'width': '50%', 'display': 'inline-block'}),
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
                        ], style={'width': '50%', 'display': 'inline-block'})
                    ])
                ])
            ])
        ], style={'height': '1200px', 'width': '1100px'}),

        html.Div([  # Stacked Bar Chart
            html.Div([
                dcc.Graph(id="stacked-bar", figure=create_stacked_bar())
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
        ]),
        html.Div(style={'height': '50px'}),
        html.Div([  # Preview dataset part
            html.Div("Bonus Plots:",
                     style={'fontSize': '30px', 'fontWeight': 'bold', 'marginTop': '5px', 'marginBottom': '5px'}),
            html.Div([
                dcc.Graph(figure=create_histogram(), style={'width': '70%', 'marginLeft': '0'})
            ], style={'padding': '20px'}),
            html.Div([
                dcc.Graph(figure=create_bad_try(), style={'display': 'inline-block', 'width': '50%'})
            ], style={'padding': '20px'})
        ]),
    ], id='right-container')
], id='container')

if __name__ == '__main__':
    app.run_server(debug=True)
