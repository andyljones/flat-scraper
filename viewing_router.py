import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import scipy as sp
from collections import OrderedDict
from itertools import product, permutations
from listing_transformer import get_listings, walking_distance
from motionless import DecoratedMap, LatLonMarker
from mapper import positions

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
listings = get_listings()
# print(shortest_path(listings))
make_map(listings)
