
import plotly_express as px
import pandas as pd
from congress_dashboard.data_loader import congress




def create_choropleth():
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
    return choropleth


def create_histogram():
    # HISTOGRAM: Age distribution
    histogram = px.histogram(
        congress,
        x='age_years',
        nbins=50,  # Number of bins
        title='Age Years Data is Normally Distributed',
        labels={'age_years': 'Age (Years)'}
    )
    return histogram

def create_stacked_bar():
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
                                 'congress': 'Congress Session',
                                 'start_date': "Start Date"},
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
    return stacked_bar

def create_bad_try():
    # graph from Analysis 2
    data2 = congress.groupby(['congress', 'party_code'])['age_years'].mean()
    data2 = data2.reset_index()
    data2.rename(columns={'age_years': 'average_age'}, inplace=True)

    # For plot21 # just find out seaborn does not work with dash
    plot21 = px.line(data2, x='congress', y='average_age', color='party_code',
                     labels={'party_code': 'Party Code',
                             'average_age': 'Average Age'},
                     title='bad try: Party-wise Average Age of Congress Members')
    return plot21