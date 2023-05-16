import pandas as pd
import requests
import json
import time
from datetime import datetime, timezone, timedelta

# Define API key
api_key = 'API_KEY'

# Define data extraction
def json_to_dataframe(json_data):
    results = json_data['results']
    data = []
    for result in results:
        row = {
            'name': result['poi']['name'],
            'lat': result['position']['lat'],
            'lon': result['position']['lon'],
            'connectorTypes': [c['connectorType'] for c in result['chargingPark']['connectors']]
        }
        if 'dataSources' in result and 'chargingAvailability' in result['dataSources']:
            row['chargingAvailability'] = result['dataSources']['chargingAvailability']['id']
        else:
            row['chargingAvailability'] = None
        data.append(row)
    df = pd.DataFrame(data)
    return df 

# Define the bbox parameters
west_longitude_min = 3.3079377
south_latitude_min = 50.7503674
east_longitude_max = 7.22749845
north_latitude_max = 53.5764232
bbox_width = 1
bbox_height = 1


# Initialize time
amsterdam_tz = timezone(timedelta(hours=1))
now = datetime.now(amsterdam_tz)
current_time = now.strftime("%Y-%m-%d_%H:%M")


# Initialize a list to store the results
results = []
results = pd.DataFrame(results)

# Loop through the bboxes
for i in range(int((east_longitude_max - west_longitude_min) // bbox_width)+1):
    for j in range(int((north_latitude_max - south_latitude_min) // bbox_height)+1):
        # Calculate the bbox coordinates
        west_longitude = west_longitude_min + i * bbox_width
        south_latitude = south_latitude_min + j * bbox_height
        east_longitude = west_longitude + bbox_width
        north_latitude = south_latitude + bbox_height

        # Set the API endpoint URL
        api_url = 'https://api.tomtom.com/search/2/categorySearch/electric%20vehicle%20station.json'
       #bbox
        topLeft = f'{north_latitude},{west_longitude}'
        btmRight = f'{south_latitude},{east_longitude}'
        # Parameters for the API request
        params = {
            'key': api_key,
            'categorySet': '7309', #categoryId
            'countrySet': 'NL',
            'minPowerKW': '40', #more than this is fastcharge (?)
            'topLeft': topLeft,
            'btmRight': btmRight,
            'limit': '100', #max 100
        }
        # Make the API request
        response = requests.get(api_url, params=params)
        print(f'{i},{j}')


        # Check if the request was successful
        if response.status_code != 200:
            print(f'Request failed with status code {response.status_code}')
            exit()

        # Parse the JSON response
        data = response.json()

        # Transform to df
        dfdata = json_to_dataframe(data)
        print(len(dfdata))
        
        # Concat
        results = pd.concat([results, dfdata], ignore_index=True)

        # Bypass 429
        time.sleep(0.5)
        
# Remove result without chargingAvailability
count = results['chargingAvailability'].notna().sum()

# Export result
results.to_csv('CP_Tomtom_NL.csv')
