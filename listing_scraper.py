import zoopla
import json
import os
import sys
import time
import requests

from image_scraper import save_photos
from bs4 import BeautifulSoup

WEEKS_PER_MONTH = 365/12./7

FIELDS_TO_STORE = [
    'listing_id',
    'status',
    'price',
    'description',
    'details_url',
    'first_published_date',
    'last_published_date',
    'agent_name',
    'agent_phone']

REQUEST_DELAY = 5#seconds
STORE_PATH = 'resources/listings.json'

def get_api():
    key = json.load(open('resources/zoopla_key.json', 'r'))
    return zoopla.api(version=1, api_key=key, cache_seconds=0)

def get_coords(station_name):
    coords = json.load(open('resources/station_coords.json', 'r'))

    if station_name in coords:
        return coords[station_name]

    long_station_name = station_name + ' Underground Station'
    if long_station_name in coords:
        return coords[long_station_name]

def get_search_params():
    params = dict(
        order_by='age',
        listing_status='rent',
        minimum_price=0,
        furnished='furnished',
        description_style=1)

    options = json.load(open('resources/search_options.json', 'r'))
    params['radius'] = options['radius']
    params['minimum_beds'] = options['beds']
    params['maximum_beds'] = options['beds']
    params['maximum_price'] = int(options['max_price']/WEEKS_PER_MONTH)

    results = {}
    for station_name in options['stations']:
        lat, lon = get_coords(station_name)
        params_for_name = params.copy()
        params_for_name['latitude'] = lat
        params_for_name['longitude'] = lon

        results[station_name] = params_for_name

    return results

def scrape_listings():
    api = get_api()
    params = get_search_params()

    results = {}
    for station_name, station_params in params.iteritems():
        yield (station_name, list(api.property_listings(**station_params)))

    return results

def scrape_property_info(page_text):
    bs = BeautifulSoup(page_text, 'html.parser')
    tag = bs.find('h3', text='Property info').find_next_sibling('ul')
    if tag:
        return tag.encode_contents()
    else:
        return ''

def store_listing(station_name, listing):
    if not os.path.exists(STORE_PATH):
        json.dump({}, open(STORE_PATH, 'w'))

    store = json.load(open(STORE_PATH, 'r'))

    listing_id = listing.listing_id
    if (listing_id not in store) or (listing.last_published_date < store[listing_id]['last_published_date']):
        print(str.format('Storing listing #{}', listing_id))
        page_text = requests.get(listing.details_url).text

        storable_listing = {field: getattr(listing, field) for field in FIELDS_TO_STORE}
        storable_listing['station_name'] = station_name
        storable_listing['photo_filenames'] = save_photos(page_text, listing_id)
        storable_listing['property_info'] = scrape_property_info(page_text)

        store[listing_id] = storable_listing

        time.sleep(REQUEST_DELAY)
    else:
        print(str.format('Listing #{} has not been updated since last time it was stored', listing_id))

    json.dump(store, open(STORE_PATH, 'r+'))

def scrape_listings_and_images():
    for i, (station_name, listings) in scrape_listings():
        print(str.format('{} listings to store for station {} of {}, {}', len(listings), i+1, len(all_listings), station_name))
        for listing in listings:
            store_listing(station_name, listing)

# sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
# scrape_listings_and_images()
