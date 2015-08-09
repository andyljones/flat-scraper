import datetime
import sys
import os

from git import Repo
from templater import generate_index
from listing_scraper import scrape_listings_and_images

def update_website():
    repo = Repo('.')
    current_branch = repo.active_branch

    print('Scraping listings...')
    scrape_listings_and_images()

    try:
        repo.heads['gh-pages'].checkout()
        print('Generating index.html...')
        generate_index()

        print('Adding to branch gh-pages...')
        repo.index.add(['index.html', 'index.css', 'photos'], force=True)
        repo.index.commit(str.format('Updated at {}', str(datetime.datetime.now())))

        print('Pushing...')
        repo.remotes['origin'].push()
        print('Pushed.')
    except Exception as e:
        print(str.format('Could not update the website. Encountered error {}', e))
    finally:
        current_branch.checkout()

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
update_website()
