import json
import scipy as sp
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
from itertools import chain
from dateutil.parser import parse
from listing_scraper import get_search_options
from listing_transformer import get_listings
from mapper import make_map

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
            a_color=get_color(listing, listings, lambda l: l['commutes']['Aldgate'], plt.cm.GnBu),
            ae_color=get_color(listing, listings, lambda l: l['commutes']['Aldgate East'], plt.cm.GnBu)
        )

def get_summary(listings):
    return dict(
        last_scrape_time=parse(max(chain(*[l['store_times'] for l in listings]))).strftime('%H:%M on %A'),
        number_of_listings=len(listings),
        number_unexpired=len([l for l in listings if not l['expired']]),
        number_of_interest=len([l for l in listings if not (l['expired'] or l['ignored'])]),
        search_options=get_search_options()
    )

def get_rendered_page():
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('index_template.html')
    listings = get_listings()
    add_colors(listings)
    make_map(listings, 'map.png')
    rendered = template.render(listings=listings, summary=get_summary(listings))
    return rendered

def generate_index():
    with open('index.html', 'w+') as f:
        f.write(get_rendered_page())

# import interactive_console_options
# generate_index()
