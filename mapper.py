import requests
import matplotlib.pyplot as plt
import seaborn as sns
import scipy as sp
from collections import OrderedDict
from PIL import Image
from StringIO import StringIO
from motionless import DecoratedMap, LatLonMarker

def positions(listings):
    return OrderedDict([(l['hashname'], (l['latitude'], l['longitude'])) for l in listings if not (l['expired'] or l['ignored'])])

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

def make_map(listings, filepath):
    sns.set_style('white')
    fig, ax = plt.subplots()
    im, labels = get_map(listings)
    ax.imshow(im)
    ax.set_xticks([])
    ax.set_yticks([])

    for i, (label, name) in enumerate(labels.items()):
        x = im.size[0] - 150
        y = 20 + i*20
        ax.text(x, y, str.format('{}: {}', label, name), fontsize=12)

    fig.set_size_inches(10, 10)

    fig.savefig(filepath, bbox_inches='tight')
    # return ax
