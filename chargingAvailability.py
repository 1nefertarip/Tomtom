import pandas as pd
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta

df = pd.read_csv('CP_Tomtom_NL.csv', dtype={'chargingAvailability': str})
#df

# TomTom API credentials
api_key = 'API_KEY'

def json_to_df(json_data):
    connectors = json_data['connectors']
    chargingAvailability = json_data['chargingAvailability']
    data = {}
    total = 0
    available = 0
    occupied = 0
    reserved = 0
    unknown = 0
    out_of_service = 0
    for connector in connectors:
        data[f"{connector['type']}_total"] = connector['total']
        data[f"{connector['type']}_available"] = connector['availability']['current']['available']
        data[f"{connector['type']}_occupied"] = connector['availability']['current']['occupied']
        data[f"{connector['type']}_reserved"] = connector['availability']['current']['reserved']
        data[f"{connector['type']}_unknown"] = connector['availability']['current']['unknown']
        data[f"{connector['type']}_out_of_service"] = connector['availability']['current']['outOfService']
        total += connector['total']
        available += connector['availability']['current']['available']
        occupied += connector['availability']['current']['occupied']
        reserved += connector['availability']['current']['reserved']
        unknown += connector['availability']['current']['unknown']
        out_of_service += connector['availability']['current']['outOfService']
    data['Total_total'] = total
    data['Total_available'] = available
    data['Total_occupied'] = occupied
    data['Total_reserved'] = reserved
    data['Total_unknown'] = unknown
    data['Total_out_of_service'] = out_of_service
    data['chargingAvailability'] = chargingAvailability
    df = pd.DataFrame(data, index=[0])
    return df

# Initialize time
amsterdam_tz = timezone(timedelta(hours=2))
now = datetime.now(amsterdam_tz)
current_time = now.strftime("%Y-%m-%d_%H:%M")

# Set the API endpoint URL
api_url = 'https://api.tomtom.com/search/2/chargingAvailability.json'

# Initialize a list to store the results
results = []
results = pd.DataFrame(results)

# Loop through the chargingAvailability values
for charging_availability in df['chargingAvailability']:
    
    # Check if charging_availability is not NaN
    if pd.notna(charging_availability):
        # Parameters for the API request
        params = {
            'key': api_key,
            'chargingAvailability': charging_availability,
            'minPowerKW': 40 #in Opencharge higher than 40 is considered a fast charge
        }

        # Make the API request
        response = requests.get(api_url, params=params)

        # Check if the request was successful
        if response.status_code != 200:
            print(f'Request failed with status code {response.status_code}')
            exit()

        # Parse the JSON response
        data = response.json()

        # Transform to dataframe
        dfdata = json_to_df(data)

        # Append to the list of results
        results = pd.concat([results, dfdata], ignore_index=True)

# results

results.to_csv(f'CP_Availability_{current_time}.csv')
