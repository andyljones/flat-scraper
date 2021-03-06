import json
import re
import scipy as sp
import humanhash
from itertools import chain
from listing_scraper import get_search_options, get_coords

WEEKS_PER_MONTH = 365/12./7
EARTH_CIRCUMFERENCE = 40075
KM_PER_MILE = 1.609
MEAN_RADIUS_OF_POINT_IN_UNIT_DISC = 2./3.
WALKING_SPEED = 5./60.#km per minute
MAX_DISTANCE_FROM_STATION_IN_KM = KM_PER_MILE*get_search_options()['radius']
MAX_DISTANCE_FROM_STATION_IN_MINS = int(MEAN_RADIUS_OF_POINT_IN_UNIT_DISC*MAX_DISTANCE_FROM_STATION_IN_KM/WALKING_SPEED)

DATE_REGEX = '(?:aug|august|sep|sept|september|oct|october|now|immediately|\d+/\d+|\d+.\d+)'
AVAILABILITY_REGEX = 'available.{,20}' + DATE_REGEX

def get_availabilities(listing):
    from_text = re.findall(AVAILABILITY_REGEX, listing['description'], flags=re.IGNORECASE)
    from_property_info = re.findall(AVAILABILITY_REGEX, listing['property_info'], flags=re.IGNORECASE)
    return from_text + from_property_info

def is_available_in_sept(listing):
    availabilities = get_availabilities(listing)
    matches = (re.findall('sep|\.09\.|\.9\.|/09/|/9/', a, flags=re.IGNORECASE) for a in availabilities)
    return True if any(matches) else False

def should_be_included(listing):
    return True if listing['photo_filenames'] and is_available_in_sept(listing) else False

def walking_distance(lat_1, lon_1, lat_2, lon_2):
    change_in_lat = EARTH_CIRCUMFERENCE*(lat_1 - lat_2)/360

    average_lat = (lat_1 + lat_2)/2
    circumference_at_lat = EARTH_CIRCUMFERENCE*sp.cos(sp.pi/180*average_lat)
    change_in_lon = circumference_at_lat*(lon_1 - lon_2)/360

    distance_in_km = sp.sqrt(change_in_lat**2 + change_in_lon**2)
    distance_in_minutes = distance_in_km/WALKING_SPEED

    return int(sp.ceil(distance_in_minutes))

def distance_from_station(lat, lon, station_name):
    station_lat, station_lon = get_coords(station_name)
    return walking_distance(lat, lon, station_lat, station_lon)

def distances_from_stations(listing):
    if 'latitude' in listing and 'longitude' in listing:
        lat, lon = listing['latitude'], listing['longitude']
        return {name: distance_from_station(lat, lon, name) for name in listing['station_name']}
    else:
        return {name: MAX_DISTANCE_FROM_STATION_IN_MINS for name in listing['station_name']}

def get_commutes(listing):
    station_names = listing['station_name']
    commutes = json.load(open('resources/commute_lengths.json', 'r'))
    a_commutes = commutes['Aldgate Underground Station']
    ae_commutes = commutes['Aldgate East Underground Station']

    distances = distances_from_stations(listing)

    return {
        'Aldgate': min(int(a_commutes[name + ' Underground Station']) + distances[name] for name in station_names),
        'Aldgate East': min(int(ae_commutes[name + ' Underground Station']) + distances[name] for name in station_names)
        }

def get_humanhash(listing):
    return humanhash.humanize(listing['listing_id'], words=2)

def is_ignored(listing):
    ignores = json.load(open('resources/ignores.json'))
    return ignores.get(get_humanhash(listing), '')

def has_expired(listing, listings):
    last_scrape_time = max(chain(*[l['store_times'] for l in listings]))
    last_store_time = max(listing['store_times'])

    listing_removed =  last_store_time < last_scrape_time
    unrentable = listing['status'] != 'to_rent'
    return listing_removed or unrentable

def sort_listings(listings):
    def key(l):
        ignored = l['expired'] or l['ignored']
        date = l['last_published_date']
        return (not ignored, date)

    return sorted(listings, key=key, reverse=True)

def get_listings():
    listings = json.load(open('resources/listings.json', 'r')).values()
    included_listings = [l for l in listings if should_be_included(l)]

    for listing in included_listings:
        listing.update(
            monthly_price=int(WEEKS_PER_MONTH*int(listing['price'])),
            availabilities=get_availabilities(listing),
            commutes=get_commutes(listing),
            hashname=get_humanhash(listing),
            expired=has_expired(listing, listings),
            ignored=is_ignored(listing),
            printable_station_names=', '.join(listing['station_name']),
            printable_availabilities=str.format('"{}"', '" or "'.join(get_availabilities(listing)))
        )

    return sort_listings(included_listings)
