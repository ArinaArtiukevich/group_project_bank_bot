import requests
import json

import numpy as np

from scipy.spatial.distance import cdist

POSITIONSTACK_API_KEY = 'd5e4e082ea5dab45f210088ac96a0822'
HERE_API_KEY = 'Q5rrnhZIet5Wp1bd2EQ23AFQx5FmYvGEa40Wkr5dYlI'

def get_coordinates(address: str):
    position_url = f'http://api.positionstack.com/v1/forward?access_key={POSITIONSTACK_API_KEY}&query={address}'
    response = requests.get(url=position_url)
    if response.ok:
        geo_data = response.json()
        return geo_data['data'][0].get('latitude'), geo_data['data'][0].get('longitude') 
    else: 
        api_key = HERE_API_KEY
        position_url = f"https://geocode.search.hereapi.com/v1/geocode?q={address}&apiKey={HERE_API_KEY}"
        response = requests.get(url=position_url)
        geo_data = response.json()
        return geo_data['items'][0].get('position')['lat'], geo_data['items'][0].get('position')['lng'] 


def nearest_atm(my_address: str) -> str:
    my_coords = get_coordinates(address = my_address)
    with open("./modules/atms_full_info.json", "r") as file:
        atms_info = json.loads(file.read())
    atms_coords = []
    for key in atms_info: 
        atms_coords.append(atms_info[key][0])
    nearest = atms_coords[np.argsort(cdist(my_coords, atms_coords))[0][0]]
    atm = [[key, atms_info[key][1], atms_info[key][2]] for key, value in atms_info.items() if value[0] == nearest][0]
    
    return f'{atm[0]}, {atm[1]}, {atm[2]}'
