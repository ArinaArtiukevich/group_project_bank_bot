import requests
import json

import numpy as np

from scipy.spatial.distance import cdist


def get_coordinates(adress: str):
    api_key = 'e070aeb5e415e5befeb62a5d9b892389'
    position_url = f'http://api.positionstack.com/v1/forward?access_key={api_key}&query=Минск, {adress}'
    response = requests.get(url=position_url)
    geo_data = response.json()
    return geo_data


# !!! atms_info - переменная, в которую должен быть записан словарь с информацией о всех банкоматах (из atms_info_generator())
def nearest_atm(my_address: str) -> str:
    my_position = get_coordinates(adress = my_address)
    my_coords = [[my_position['data'][0].get('latitude'), my_position['data'][0].get('longitude')]]
    with open("./modules/atms_full_info.json", "r") as file:
        atms_info = json.loads(file.read())
    atms_coords = []
    for key in atms_info: 
        atms_coords.append(atms_info[key][0])
    nearest = atms_coords[np.argsort(cdist(my_coords, atms_coords))[0][0]]
    atm = [[key, atms_info[key][1], atms_info[key][2]] for key, value in atms_info.items() if value[0] == nearest][0]
    
    return f'{atm[0]}, {atm[1]}, {atm[2]}'
