import zoopla
import json
import os
import datetime
import time
import requests
import logging

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

REQUEST_DELAY = 1#seconds
CACHE_LENGTH = 3*60*60#seconds
STORE_PATH = 'resources/listings.json'

def get_api():
    key = json.load(open('resources/zoopla_key.json', 'r'))
    return zoopla.api(version=1, api_key=key, cache_seconds=CACHE_LENGTH)

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

def scrape_property_info(page_text):
    bs = BeautifulSoup(page_text, 'html.parser')
    tag = bs.find('h3', text='Property info').find_next_sibling('ul')
    if tag:
        return tag.encode_contents()
    else:
        return ''

def create_storable_listing(station_name, start_time, listing):
    page_text = requests.get(listing.details_url).text

    return dict(
        {field: getattr(listing, field) for field in FIELDS_TO_STORE},
        station_name=[station_name],
        photo_filenames=save_photos(page_text, listing.listing_id),
        property_info=scrape_property_info(page_text),
        store_times=[str(start_time)]
    )

def update_storable_listing(station_name, start_time, stored_listing, listing):
    storable_listing = create_storable_listing(station_name, start_time, listing)
    storable_listing['station_name'] = list(set(stored_listing['station_name']).union(stored_listing['station_name']))
    storable_listing['store_times'] = list(set(stored_listing['store_times']).union(stored_listing['store_times']))

    return storable_listing

def store_listing(station_name, start_time, listing):
    if not os.path.exists(STORE_PATH):
        json.dump({}, open(STORE_PATH, 'w'))

    store = json.load(open(STORE_PATH, 'r'))
    listing_id = listing.listing_id
    stored_listing = store.get(listing_id)

    if not stored_listing:
        logging.info(str.format('Storing listing #{}', listing_id))
        stored_listing = create_storable_listing(station_name, start_time, listing)
        time.sleep(REQUEST_DELAY)
    elif (listing.last_published_date > stored_listing['last_published_date']):
        logging.info(str.format('Updating listing #{}', listing_id))
        stored_listing = update_storable_listing(station_name, start_time, stored_listing, listing)
        time.sleep(REQUEST_DELAY)
    else:
        logging.info(str.format('No change in listing #{}', listing_id))
        stored_listing['station_name'] = list(set(stored_listing['station_name']).union([station_name]))
        stored_listing['store_times'] = list(set(stored_listing['store_times']).union([str(start_time)]))

    store[listing_id] = stored_listing

    backup = json.load(open(STORE_PATH, 'r'))
    try:
        json.dump(store, open(STORE_PATH, 'w'))
    except Exception as e:
        logging.warning(str.format('Could not save the updated store. Returning to backup. Exception {}', e))
        json.dump(backup, open(STORE_PATH, 'w'))

def scrape_listings_and_images():
    time =  datetime.datetime.now()
    for i, (station_name, listings) in enumerate(scrape_listings()):
        logging.info(str.format('{} listings to store for station {}, {}', len(listings), i+1, station_name))
        for listing in listings:
            store_listing(station_name, time, listing)

import interactive_console_options
scrape_listings_and_images()
