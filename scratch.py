import zoopla
import json

def get_api():
    key = json.load(open('resources/zoopla_key.json', 'r'))
    return zoopla.api(version=1, api_key=key)

def get_coords_of_interest():
    stations_of_interest = json.load('resources/stations_of_interest.json')
    coords = json.load('resources/station_coords.json')

    results = {}
    for station_name in stations_of_interest:
        if station_name in coords:
            results[station_name] = coords[station_name]

        long_station_name = station_name + ' Underground Station'
        if long_station_name in coords:
            results[station_name] = coords[long_station_name]

    return results
