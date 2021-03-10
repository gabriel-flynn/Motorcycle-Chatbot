# Script to scrape motorcyclenews.com for reviews
import pickle
import urllib.request
from os import mkdir
from time import sleep
from urllib.error import HTTPError
from urllib.parse import urljoin

from bs4 import BeautifulSoup

base_url = "https://www.motorcyclenews.com"
data_folder = 'data'
mcn_folder = 'mcn'
html_folder = 'html'


def build_url(page_number):
    return f"https://www.motorcyclenews.com/bike-reviews/search-results/?page={page_number}"


def scrape_review_urls():
    try:
        mkdir(data_folder)
    except FileExistsError:
        pass
    try:
        mkdir(f'{data_folder}/{mcn_folder}')
    except FileExistsError:
        pass

    review_urls = set()
    page = 1
    while True:
        try:
            url = build_url(page)
            data = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(data, features="html.parser")
            links = [urljoin(base_url, a['href']) for a in soup.select("ul.search-results__list a[href]")]
            review_urls.update(links)
            page += 1
            print(links)
            sleep(1)
        except HTTPError:
            print(page)
            pickle.dump(review_urls, open(f'{data_folder}/{mcn_folder}/review_urls.pickle', 'wb'))
            break


def scrape_review_html_pages():
    try:
        mkdir(f'{data_folder}/{mcn_folder}/{html_folder}')
    except FileExistsError:
        pass

    review_urls = pickle.load(open(f'{data_folder}/{mcn_folder}/review_urls.pickle', 'rb'))
    for url in review_urls:
        bike_review_path = 'bike-reviews/'
        html_file_name = url[url.find(bike_review_path) + len(bike_review_path):].replace('/', '-')[:-1] + '.html'
        urllib.request.urlretrieve(url, f'{data_folder}/{mcn_folder}/{html_file_name}')
        print(f'Created html file for {url} called {html_file_name}')
        sleep(1)


if __name__ == "__main__":
    # uncomment to regenerate review or html pages
    # scrape_review_urls()
    # scrape_review_html_pages()
    pass
