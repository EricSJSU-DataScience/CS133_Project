import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
import certifi
import ssl
import urllib.request
import wikipediaapi
from dash.dependencies import Input, Output, State

url = 'https://raw.githubusercontent.com/fivethirtyeight/data/refs/heads/master/congress-demographics/data_aging_congress.csv'

# Create SSL context using certifi
context = ssl.create_default_context(cafile=certifi.where())

# Use urllib to open the URL
with urllib.request.urlopen(url, context=context) as response:
    congress = pd.read_csv(response)
    print(congress.head(3))  # make sure data was loaded properly

# Initialize Wikipedia API with a user agent
user_agent = "MyApp/1.0 (https://myappwebsite.example)"
wiki = wikipediaapi.Wikipedia('en', headers={'User-Agent': user_agent})


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
    'age_years'].mean(

).reset_index()
data_c.rename(columns={'age_years': 'average_age'}, inplace=True)
data_c.sort_values(by='congress', inplace=True)
choropleth = px.choropleth(data_c,
                           locations='state_abbrev',
                           locationmode='USA-states',
                           # Map mode set to US states
                           color='average_age',
                           color_continuous_scale='Reds',
                           scope='usa',
                           range_color=(50, 62),
                           hover_name='state_abbrev',
                           labels={'state_abbrev': 'State Abbreviations',
                                   'average_age': 'Average Age of Congress Members',
                                   'congress': 'Number of the Congress'},
                           title='Average Age of Congress Members by State',
                           animation_frame='congress'
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

# AVERAGE AGE LINE GRAPH
data_l = congress.groupby('congress')['age_years'].mean()
data_l = data_l.reset_index()
data_l.rename(columns={'age_years': 'average_age'}, inplace=True)
line_combined = px.line(data_l, x='congress', y='average_age',
                        title='Average age of Congress members over time')

# AVERAGE AGE NEW VS RETURNING LINE GRAPH
# Classify each member as 'New' if cmltv_cong == 1, otherwise 'Returning'
congress['member_type'] = congress['cmltv_cong'].apply(
    lambda x: 'New' if x == 1 else 'Returning')

# Calculate the average age for new vs. returning members per session
avg_age_by_member_type = congress.groupby(['congress', 'member_type'])[
    'age_years'].mean().reset_index()

# Create line plot
new_vs_returning = px.line(avg_age_by_member_type, x='congress',
                           y='age_years', color='member_type',
                           title='Average Age of New vs. Returning Members by Session')

app = Dash(__name__)
app.layout = html.Div([
    html.Div([  # Here are the html components in the left pane
        html.H1("Is Congress Getting Older?"),
        html.P("Exploring the age trends of US Congress Members"),
        html.Img(src="assets/congress_seal.png"),
        html.Label("Chamber of Congress", className='dropdown-labels'),
        dcc.Dropdown(id='chamber-dropdown', className='dropdown', multi=True,
                     options=create_dropdown_options(
                         pd.Series(['Senate', 'House'])),
                     value=create_dropdown_value(pd.Series(['Senate', 'House']))
                     ),
        html.Label("Party", className='dropdown-labels'),
        dcc.Dropdown(id='party-dropdown', className='dropdown', multi=True,
                     options=create_dropdown_options(
                         pd.Series(['Democrat', 'Republican'])),
                     value=create_dropdown_value(
                         pd.Series(['Democrat', 'Republican']))
                     ),
        html.Button(id='update-button', children="Update"),
        html.Hr(),  # Horizontal line for separation
        html.H2("Search Wikipedia"),
        dcc.Input(id='name-input', type='text', placeholder='Enter a name'),
        html.Button('Search Wikipedia', id='search-button', n_clicks=0),
        html.Div(id='wikipedia-summary',
                 children="Wikipedia Summary:\nEnter a name to see the Wikipedia summary here.")
    ], style={'width': '20%', 'display': 'inline-block',
              'verticalAlign': 'top'}),
    html.Div([  # Here are the html components in the right pane
        html.Div([  # two plots on the top
            dcc.Graph(figure=line_combined, style={'display': 'inline-block',
                                                   'width':
                                                       '49%'}),
            dcc.Graph(figure=new_vs_returning, style={'display': 'inline-block',
                                                      'width': '49%'})
        ]),
        html.Div([  # table, switches, and slider on the bottom
            dcc.Graph(id="stacked-bar", figure=stacked_bar),
            html.Div([
                dcc.Graph(id="choropleth", figure=choropleth)
            ]),
        ])
    ], style={'width': '75%', 'display': 'inline-block',
              'padding-left': '20px'})
], id='container')


# Callback for Wikipedia search
@app.callback(
    Output('wikipedia-summary', 'children'),
    Input('search-button', 'n_clicks'),
    State('name-input', 'value')
)
def search_wikipedia(n_clicks, name):
    if n_clicks > 0 and name:
        try:
            page = wiki.page(name)
            if page.exists():
                summary = page.summary[:500] + "..."
            else:
                summary = "No page found for this name."
        except Exception as e:
            summary = f"An error occurred: {e}"
    else:
        summary = "Enter a name to see the Wikipedia summary here."
    return f"### Wikipedia Summary:\n{summary}"


if __name__ == '__main__':
    app.run_server(debug=True)
