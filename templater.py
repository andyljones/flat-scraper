import json
import scipy as sp
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import re
import humanhash
from jinja2 import Environment, FileSystemLoader
from itertools import chain
from dateutil.parser import parse
from listing_scraper import get_coords, get_search_options

WEEKS_PER_MONTH = 365/12./7
EARTH_CIRCUMFERENCE = 40075
KM_PER_MILE = 1.609
MEAN_RADIUS_OF_POINT_IN_UNIT_DISC = 2./3.
WALKING_SPEED = 5./60.#km per minute
MAX_DISTANCE_FROM_STATION_IN_KM = KM_PER_MILE*get_search_options()['radius']
MAX_DISTANCE_FROM_STATION_IN_MINS = int(MEAN_RADIUS_OF_POINT_IN_UNIT_DISC*MAX_DISTANCE_FROM_STATION_IN_KM/WALKING_SPEED)


DATE_REGEX = '(?:aug|august|sep|sept|september|oct|october|now|immediately|\d+/\d+|\d+.\d+)'
AVAILABILITY_REGEX = 'available.{,20}' + DATE_REGEX

def get_color(listing, listings, f, cm):
    price = f(listing)
    prices = [f(l) for l in listings]

    lower = sp.percentile(prices, 10)
    upper = sp.percentile(prices, 90)

    relative_price = (price - lower)/(upper - lower)
    color = cm(sp.clip(relative_price, 0, 1))

    is_dark = sum(color[:3])/4 < 0.4
    background_color = tuple([int(255*c) for c in color[:3]])
    text_color = (230, 230, 230) if is_dark else (50, 50, 50)

    return background_color, text_color

def add_colors(listings):
    for listing in listings:
        listing.update(
            price_color=get_color(listing, listings, lambda l: int(l['price']), plt.cm.YlOrRd),
            euston_color=get_color(listing, listings, lambda l: l['commutes']['Euston'], plt.cm.GnBu),
            green_park_color=get_color(listing, listings, lambda l: l['commutes']['Green Park'], plt.cm.GnBu)
        )

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

def distance_from_station(lat, lon, station_name):
    station_lat, station_lon = get_coords(station_name)

    change_in_lat = EARTH_CIRCUMFERENCE*(lat - station_lat)/360

    average_lat = (lat + station_lat)/2
    circumference_at_lat = EARTH_CIRCUMFERENCE*sp.cos(sp.pi/180*average_lat)
    change_in_lon = circumference_at_lat*(lon - station_lon)/360

    distance_in_km = sp.sqrt(change_in_lat**2 + change_in_lon**2)
    distance_in_minutes = distance_in_km/WALKING_SPEED

    return int(sp.ceil(distance_in_minutes))


def distances_from_stations(listing):
    if 'latitude' in listing and 'longitude' in listing:
        lat, lon = listing['latitude'], listing['longitude']
        return {name: distance_from_station(lat, lon, name) for name in listing['station_name']}
    else:
        return {name: MAX_DISTANCE_FROM_STATION_IN_MINS for name in listing['station_name']}

def get_commutes(listing):
    station_names = listing['station_name']
    commutes = json.load(open('resources/commute_lengths.json', 'r'))
    euston_commutes = commutes['Euston Underground Station']
    green_park_commutes = commutes['Green Park Underground Station']

    distances = distances_from_stations(listing)

    return {
        'Euston': min(int(euston_commutes[name + ' Underground Station']) + distances[name] for name in station_names),
        'Green Park': min(int(green_park_commutes[name + ' Underground Station']) + distances[name] for name in station_names)
        }

def has_expired(listing, listings):
    last_scrape_time = max(chain(*[l['store_times'] for l in listings]))
    last_store_time = max(listing['store_times'])

    listing_removed =  last_store_time < last_scrape_time
    unrentable = listing['status'] != 'to_rent'
    return listing_removed or unrentable

def get_listings():
    listings = json.load(open('resources/listings.json', 'r')).values()
    included_listings = [l for l in listings if should_be_included(l)]

    for listing in included_listings:
        listing.update(
            monthly_price=int(WEEKS_PER_MONTH*int(listing['price'])),
            availabilities=get_availabilities(listing),
            commutes=get_commutes(listing),
            hashname=humanhash.humanize(listing['listing_id'], words=2),
            expired=has_expired(listing, listings),
            printable_station_names=', '.join(listing['station_name']),
            printable_availabilities=str.format('"{}"', '" or "'.join(get_availabilities(listing)))
        )

    add_colors(included_listings)

    return sorted(included_listings, key=lambda r: r['last_published_date'], reverse=True)

def get_summary(listings):
    return dict(
        last_scrape_time=parse(max(chain(*[l['store_times'] for l in listings]))).strftime('%H:%M on %A'),
        number_of_listings=len(listings),
        number_unexpired=len([l for l in listings if not l['expired']]),
        search_options=get_search_options()
    )

def get_rendered_page():
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('index_template.html')
    listings = get_listings()
    rendered = template.render(listings=listings, summary=get_summary(listings))
    return rendered

def generate_index():
    with open('index.html', 'w+') as f:
        f.write(get_rendered_page())

# import interactive_console_options
# generate_index()
