import json
import scipy as sp
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
from jinja2 import Environment, FileSystemLoader

WEEKS_PER_MONTH = 365/12./7

def get_listing_color(listing, listings):
    price = int(listing['price'])
    prices = [int(l['price']) for l in listings]

    lower = sp.percentile(prices, 10)
    upper = sp.percentile(prices, 90)

    relative_price = (price - lower)/(upper - lower)
    color = plt.cm.YlOrRd(sp.clip(relative_price, 0, 1))

    return tuple([int(255*c) for c in color])

def get_listings():
    listings = json.load(open('resources/listings.json', 'r'))
    results = []
    for listing in listings.values():
        if listing['photo_filenames']:
            listing['monthly_price'] = int(WEEKS_PER_MONTH*int(listing['price']))
            listing['color'] = get_listing_color(listing, listings.values())
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
