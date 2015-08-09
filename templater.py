import json
import scipy as sp
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import re
import humanhash
from jinja2 import Environment, FileSystemLoader

WEEKS_PER_MONTH = 365/12./7

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

def get_commutes(station_names):
    commutes = json.load(open('resources/commute_lengths.json', 'r'))
    euston_commutes = commutes['Euston Underground Station']
    green_park_commutes = commutes['Green Park Underground Station']

    return {
        'Euston': min(int(euston_commutes[name + ' Underground Station']) for name in station_names),
        'Green Park': min(int(green_park_commutes[name + ' Underground Station']) for name in station_names)
        }

def get_listings():
    listings = json.load(open('resources/listings.json', 'r')).values()
    results = []
    for listing in listings:
        if should_be_included(listing):
            listing['monthly_price'] = int(WEEKS_PER_MONTH*int(listing['price']))
            listing['availabilities'] = get_availabilities(listing)
            listing['commutes'] = get_commutes(listing['station_name'])
            listing['hashname'] = humanhash.humanize(listing['listing_id'], words=2)
            results.append(listing)

    for listing in results:
        listing['price_color'] = get_color(listing, results, lambda l: int(l['price']), plt.cm.YlOrRd)
        listing['euston_color'] = get_color(listing, results, lambda l: l['commutes']['Euston'], plt.cm.GnBu)
        listing['green_park_color'] = get_color(listing, results, lambda l: l['commutes']['Green Park'], plt.cm.GnBu)

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
