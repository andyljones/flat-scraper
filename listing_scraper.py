import zoopla
import json

WEEKS_PER_MONTH = 365/12./7

def get_api():
    key = json.load(open('resources/zoopla_key.json', 'r'))
    return zoopla.api(version=1, api_key=key)

def get_coords(station_name):
    coords = json.load(open('resources/station_coords.json', 'r'))

    if station_name in coords:
        return coords[station_name]

    long_station_name = station_name + ' Underground Station'
    if long_station_name in coords:
        return coords[long_station_name]

def get_search_params():
    params = dict(order_by='age', listing_status='rent', furnished='furnished')

    options = json.load(open('resources/search_options.json', 'r'))
    params['radius'] = options['radius']
    params['minimum_beds'] = options['beds']
    params['maximum_beds'] = options['beds']
    params['maximum_price'] = options['max_price']/WEEKS_PER_MONTH

    results = {}
    for station_name in options['stations']:
        lat, lon = get_coords(station_name)
        params_for_name = params.copy()
        params_for_name['latitude'] = lat
        params_for_name['longitude'] = lon

        results[station_name] = params_for_name

    return results

def scrape():
    api = get_api()
    params = get_search_params()

    results = {}
    for station_name, station_params in params.iteritems():
        results[station_name] = list(api.property_listings(**station_params))

    return results
