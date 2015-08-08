import json
from jinja2 import Environment, FileSystemLoader

listings = json.load(open('resources/listings.json', 'r'))

env = Environment(loader=FileSystemLoader('resources'))
template = env.get_template('index_template.html')
rendered = template.render(listings=listings)

with open('resources/index.html', 'w+') as f:
    f.write(rendered)
