import requests
import os
from bs4 import BeautifulSoup
from StringIO import StringIO
from PIL import Image

TEST_URL = 'http://www.zoopla.co.uk/to-rent/details/37701239'
TEST_PHOTO_URL = 'http://li.zoocdn.com/234544bd101eab23ede830a9a238d1afede05c1a_645_430.jpg'

def get_photo_urls(page_text):
    bs = BeautifulSoup(page_text, 'html.parser')
    thumbnail_tags = bs.find_all(class_="images-thumb")
    photo_urls = [tag.attrs['data-photo'] for tag in thumbnail_tags]
    return photo_urls

def save_photo(photo_url, filename):
    photo_string = requests.get(photo_url).content
    photo = Image.open(StringIO(photo_string))

    if not os.path.exists('photos'):
        os.mkdir('photos')

    try:
        photo.save(os.path.join('photos', filename))
    except Exception as e:
        print(str.format('Failed to save photo at {} with filename {}. Exception: {}', photo_url, filename, e))

def save_photos(page_text, listing_id):
    photo_urls = get_photo_urls(page_text)
    filenames = []
    for i, url in enumerate(photo_urls):
        filename = str.format('{}_{}.jpg', listing_id, i)
        filenames.append(filename)
        save_photo(url, filename)

    return filenames
