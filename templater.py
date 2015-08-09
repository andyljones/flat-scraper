import json
import scipy as sp
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import re
from jinja2 import Environment, FileSystemLoader

WEEKS_PER_MONTH = 365/12./7

DATE_REGEX = '(?:aug|august|sep|sept|september|oct|october|now|immediately|\d+/\d+|\d+.\d+)'
AVAILABILITY_REGEX = 'available.{,20}' + DATE_REGEX

def get_price_color(listing, listings):
    price = int(listing['price'])
    prices = [int(l['price']) for l in listings]

    lower = sp.percentile(prices, 10)
    upper = sp.percentile(prices, 90)

    relative_price = (price - lower)/(upper - lower)
    color = plt.cm.YlOrRd(sp.clip(relative_price, 0, 1))

    return tuple([int(255*c) for c in color])

def get_availabilities(listing):
    from_text = re.findall(AVAILABILITY_REGEX, listing['description'], flags=re.IGNORECASE)
    from_property_info = re.findall(AVAILABILITY_REGEX, listing['property_info'], flags=re.IGNORECASE)

    return from_text + from_property_info

def is_available_in_sept(listing):
    availabilities = get_availabilities(listing)
    if any(re.findall('sep|\.09\.|\.9\.|/09/|/9/', a, flags=re.IGNORECASE) for a in availabilities):
        return True

def should_be_included(listing):
    if listing['photo_filenames'] and is_available_in_sept(listing):
        return True

def get_commutes(station_name):
    commutes = json.load(open('resources/commute_lengths.json', 'r'))
    return {
        'Euston': commutes['Euston Underground Station'][station_name + ' Underground Station'],
        'Green Park': commutes['Green Park Underground Station'][station_name + ' Underground Station']
        }

def get_listings():
    listings = json.load(open('resources/listings.json', 'r'))
    results = []
    for listing in listings.values():
        if should_be_included(listing):
            listing['monthly_price'] = int(WEEKS_PER_MONTH*int(listing['price']))
            listing['price_color'] = get_price_color(listing, listings.values())
            listing['availabilities'] = get_availabilities(listing)
            listing['commutes'] = get_commutes(listing['station_name'])
            results.append(listing)

    results = sorted(results, key=lambda r: r['last_published_date'], reverse=True)

    return results

def get_rendered_page():
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('index_template.html')
    rendered = template.render(listings=get_listings())
    return rendered

def generate_index():
    with open('index.html', 'w+') as f:
        f.write(get_rendered_page())

generate_index()
