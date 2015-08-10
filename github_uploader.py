import datetime
import logging

from git import Repo
from templater import generate_index
from listing_scraper import scrape_listings_and_images

def update_website():
    repo = Repo('.')
    current_branch = repo.active_branch

    logging.info('Scraping listings...')
    scrape_listings_and_images()

    try:
        repo.heads['gh-pages'].checkout()
        logging.info('Generating index.html...')
        generate_index()

        logging.info('Adding to branch gh-pages...')
        repo.index.add(['index.html', 'index.css', 'photos'], force=True)
        repo.index.commit(str.format('Updated at {}', str(datetime.datetime.now())))

        logging.info('Pushing...')
        repo.remotes['origin'].push()
        logging.info('Pushed.')
    except Exception as e:
        logging.warning(str.format('Could not update the website. Encountered error {}', e))
    finally:
        current_branch.checkout()

import interactive_console_options
update_website()
