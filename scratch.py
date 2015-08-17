from listing_transformer import get_listings
import scipy as sp
import pandas as pd

def get_interesting_listings():
    return [l for l in get_listings() if not (l['expired'] or l['ignored'])]

def essential_stats(listings):
    df = pd.DataFrame(index=[l['hashname'] for l in listings], columns=['rent', 'euston', 'green'])
    for l in listings:
        df.loc[l['hashname']] = [l['monthly_price'], l['commutes']['Euston'], l['commutes']['Green Park']]

    return df

def find_dominated(listings):
    stats = essential_stats(listings)
    dominated = {}
    for name, row in stats.iterrows():
        beat_by = stats.loc[(stats < row).all(1)]
        if (stats < row).all(1).any():
            print name, row - beat_by

listings = get_interesting_listings()
print(find_dominated(listings))
