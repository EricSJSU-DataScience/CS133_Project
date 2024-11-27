import pandas as pd
import ssl
import certifi
import urllib.request

# Function to load congress data
def load_congress_data():
    url = 'https://raw.githubusercontent.com/fivethirtyeight/data/refs/heads/master/congress-demographics/data_aging_congress.csv'
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(url, context=context) as response:
        return pd.read_csv(response)

# Function to load party info data
def load_party_info():
    return pd.read_csv("assets/party_codes.csv")

def modified_data():
    congress_data = load_congress_data()
    # Classify each member as 'New' if cmltv_cong == 1, otherwise 'Returning'
    congress_data['member_type'] = congress_data['cmltv_cong'].apply(
        lambda x: 'New' if x == 1 else 'Returning')
    return congress_data

def calculate_avg_age_by_member_type(data):
    # Calculate the average age for new vs. returning members per session
    avg_age_data = data.groupby(['congress', 'member_type'])['age_years'].mean().reset_index()
    return avg_age_data


# Load datasets
congress = modified_data()
party_info = load_party_info()



