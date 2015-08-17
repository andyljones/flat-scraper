import requests
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import scipy as sp
from collections import OrderedDict
from itertools import product, permutations
from PIL import Image
from StringIO import StringIO
from templater import get_listings, walking_distance
from motionless import DecoratedMap, LatLonMarker

def positions(listings):
    coords = {l['hashname']: (l['latitude'], l['longitude']) for l in listings if not (l['expired'] or l['ignored'])}
    sorted_coords = sorted(coords.items(), key=lambda (name, (lat, lon)): lat)
    return OrderedDict(sorted_coords)

def get_map_url(listings):
    dmap = DecoratedMap(size_x=640, size_y=640)
    labels = OrderedDict()
    for i, (name, (lat, lon)) in enumerate(positions(listings).items()):
        label = chr(ord('A') + i)
        labels[label] = name
        dmap.add_marker(LatLonMarker(lat, lon, label=label))
    return dmap.generate_url(), labels

def get_map(listings):
    url, labels = get_map_url(listings)
    data = StringIO(requests.get(url).content)
    return Image.open(data), labels

def make_map(listings):
    sns.set_style('white')
    fig, ax = plt.subplots()
    im, labels = get_map(get_listings())
    ax.imshow(im)
    ax.set_xticks([])
    ax.set_yticks([])

    for i, (label, name) in enumerate(labels.items()):
        x = im.size[0] - 150
        y = 20 + i*20
        ax.text(x, y, str.format('{}: {}', label, name), fontsize=12)

    figure.set_size_inches(10, 10)
    return ax


def pairwise_distances(listings):
    coords = positions(listings)
    distances = pd.DataFrame(index=coords.keys(), columns=coords.keys())
    for name_1, name_2 in product(coords.keys(), coords.keys()):
        lat_1, lon_1 = coords[name_1]
        lat_2, lon_2 = coords[name_2]
        distances.loc[name_1, name_2] = walking_distance(lat_1, lon_1, lat_2, lon_2)

    return distances

def shortest_path(listings):
    distances = pairwise_distances(listings)
    best = None
    best_time = sp.inf
    for p in permutations(distances.index):
        time = sum(distances.at[s, t] for s, t in zip(p, p[1:]))
        if time < best_time:
            best = p
            best_time = time

    times_of_best = [distances.at[s, t] for s, t in zip(best, best[1:])]
    return best, times_of_best, best_time

# %matplotlib inline
# listings = get_listings()
# print(shortest_path(listings))
# make_map(listings)
