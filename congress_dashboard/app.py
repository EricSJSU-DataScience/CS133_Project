## require:
## pip install wikipedia-api
## pip install dash

import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
import certifi
import ssl
import urllib.request
import panel as pn
import panel.widgets as pnw
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
## add more info to Geo map
# dataset: get number of house by different year
temp=congress[congress['chamber'] == 'House'].groupby(by=['state_abbrev', 'congress'])['age_years'].size().reset_index()
temp.rename(columns={'age_years': 'number_of_house'}, inplace=True)
# dataset: get number of senate by different year
temp1=congress[congress['chamber'] == 'Senate'].groupby(by=['state_abbrev', 'congress'])['age_years'].size().reset_index()
temp1.rename(columns={'age_years': 'number_of_senate'}, inplace=True)
# merge them then merge to main Geo dataset
temp = temp.merge(temp1, left_on=['state_abbrev', 'congress'], right_on=['state_abbrev', 'congress'])
data_c = data_c.merge(temp, left_on=['state_abbrev', 'congress'], right_on=['state_abbrev', 'congress'])


choropleth = px.choropleth(data_c,
                           locations='state_abbrev',
                           locationmode='USA-states', # Map mode set to US states
                           color='average_age',
                           color_continuous_scale='Reds',
                           scope='usa',
                           range_color=(50, 62),
                           hover_name='state_abbrev',
                           hover_data={'number_of_house': True, 'number_of_senate': True},
                           labels={'state_abbrev': 'State Abbreviations',
                              'average_age': 'Average Age of Congress Members',
                              'congress': 'Number of the Congress',
                              'number_of_house': 'Number of House',
                              'number_of_senate': 'Number of Senate'},
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
            ], style={'padding': '20px'}),
        ]),
        # try to add another section for table
        html.Div([
            html.H2('Filter options'),
            html.Div([
                html.Label('Congress:'),
                dcc.Dropdown(id='select-congress', options=[{'label': val, 'value': val} for val in list_default + sorted(congress['congress'].unique().tolist())], value='Default'),
                html.Label('Chamber:'),
                dcc.Dropdown(id='select-chamber', options=[{'label': val, 'value': val} for val in list_default + sorted(congress['chamber'].unique().tolist())], value='Default'),
                html.Label('State:'),
                dcc.Dropdown(id='select-state', options=[{'label': val, 'value': val} for val in list_default + sorted(congress['state_abbrev'].unique().tolist())], value='Default'),
                html.Label('Party Code:'),
                dcc.Dropdown(id='select-party', options=[{'label': val, 'value': val} for val in list_default + sorted(congress['party_code'].unique().tolist())], value='Default'),
                html.Label('Age Range:'),
                dcc.RangeSlider(id='age-slider', min=20, max=100, value=[20, 100], marks={i: str(i) for i in range(20, 101, 10)})
            ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ]),
        html.Div([
            html.Div([
                    html.H2('Data After Filter'),
                    dash_table.DataTable(id='filtered-table', 
                                         columns=[{"name": i, "id": i} for i in congress.columns],
                                         page_size=10,
                                         row_selectable='single')
                ], style={'width': '70%', 'display': 'inline-block'}),
                html.Div([
                    html.H3('Selected Bioname:'),
                    html.Div(id='selected-bioname'),
                    html.Button('Search Wikipedia', id='search-wikipedia', n_clicks=0)
                ], style={'padding-top': '20px', 'backgroundColor': '#e0e0e0'}),
                html.Div(id='wikipedia-summary-table', style={'padding-top': '20px', 'backgroundColor': '#e0e0e0'})
        ], style={'padding-bottom': '200px'})
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

#### try to add another section for table 
@app.callback(
    Output('filtered-table', 'data'),
    Input('select-congress', 'value'),
    Input('select-chamber', 'value'),
    Input('select-state', 'value'),
    Input('select-party', 'value'),
    Input('age-slider', 'value')
)

def update_filtered_data(arg_congress, arg_chamber, arg_state, arg_party, arg_age):
    res = congress.copy()
    if arg_congress != 'Default':
        res = res[res['congress'] == arg_congress]
    if arg_chamber != 'Default':
        res = res[res['chamber'] == arg_chamber]
    if arg_state != 'Default':
        res = res[res['state_abbrev'] == arg_state]
    if arg_party != 'Default':
        res = res[res['party_code'] == arg_party]
    res = res[(res['age_years'] >= arg_age[0]) & (res['age_years'] <= arg_age[1])]
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
