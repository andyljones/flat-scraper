import json
from jinja2 import Environment, FileSystemLoader

WEEKS_PER_MONTH = 365/12./7

def get_filtered_listings():
    listings = json.load(open('resources/listings.json', 'r'))
    results = []
    for listing in listings.values():
        if listing['photo_filenames']:
            listing['price'] = int(WEEKS_PER_MONTH*int(listing['price']))
            results.append(listing)

    return results

def get_rendered_page():
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('index_template.html')
    rendered = template.render(listings=get_filtered_listings())
    return rendered

with open('index.html', 'w+') as f:
    f.write(get_rendered_page())
