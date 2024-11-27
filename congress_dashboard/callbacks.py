import plotly_express as px
import wikipediaapi
from dash.dependencies import Input, Output, State
from app_instance import app
from congress_dashboard.data_loader import congress, party_info, calculate_avg_age_by_member_type


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
