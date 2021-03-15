# Script to scrape motorcyclenews.com for reviews
import pickle
import re
import sys
import urllib.request
from os import mkdir, listdir
from os.path import isfile, join
from time import sleep
from urllib.error import HTTPError
from urllib.parse import urljoin

from bs4 import BeautifulSoup

base_url = "https://www.motorcyclenews.com"
data_folder = 'data'
mcn_folder = 'mcn'
html_folder = 'html'

# There's an Enfield and Royal Enfield - should that be treated the same? Not really familiar with those bikes
manufacturers = ["APRILIA", "ARTISAN", "BIMOTA", "BMW", "BENELLI", "CAGIVA", "CF MOTO", "ENFIELD", "DERBI", "DUCATI",
                 "GILERA", "HARLEY-DAVIDSON",
                 "HESKETH", "HUSQVARNA", "HONDA", "LEXMOTO", "KAWASAKI", "KTM", "MZ", "MONDIAL", "MOTO-GUZZI", "MORINI",
                 "MV-AGUSTA", "PIAGGIO", "PEUGEOT",
                 "RIEJU", "ROYAL ENFIELD", "SHERCO", "SUZUKI", "SWM", "TRIUMPH", "VICTORY", "YAMAHA", "WK BIKES",
                 "ZONTES"]


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


def extractModelAndYear(model_and_year):
    # MCN doesn't include the year for some reason for the 72
    if model_and_year == "HARLEY-DAVIDSON XL1200 SPORTSTER 72":
        model_and_year = "HARLEY-DAVIDSON XL1200 SPORTSTER 72 (2012 - 2016)"

    matches = re.findall(r"^([\w\-]+) ([\w\-\s./&+]+) \(([\d]+)\s?-\s?([\w]+)\)", model_and_year)[0]

    manufacturer = ""
    model = ""
    year_start = 1800
    year_end = 1800

    curr_string = ""
    found_manufacturer = False
    for index, match in enumerate(matches, start=0):
        if not found_manufacturer:
            if match in manufacturers:
                manufacturer = match
                found_manufacturer = True
                curr_string = ""
            elif f'{curr_string} {match.split(" ")[0]}' in manufacturers:
                manufacturer = curr_string + match.split(" ")[0]
                found_manufacturer = True
                curr_string = match.replace(match.split(" ")[0], "")
            else:
                curr_string += match
        if found_manufacturer and index >= 1:
            if match.isnumeric() and len(match) == 4:
                model = curr_string
                year_start = int(match)
                year_end = matches[index + 1]
                break
            else:
                curr_string += match

    return manufacturer, model, year_start, year_end


def parseHtml():
    path = f'{data_folder}/{mcn_folder}/{html_folder}'
    files = [f for f in listdir(path) if isfile(join(path, f))]

    for file in files:
        html = BeautifulSoup(open(f'{path}/{file}'))

        # Extract model and year
        model_and_year = html.find("h1").text.upper().replace("REVIEW", "")
        print(model_and_year)
        manufacturer, model, year_start, year_end = extractModelAndYear(model_and_year)


if __name__ == "__main__":
    # uncomment to regenerate review or html pages
    # scrape_review_urls()
    # scrape_review_html_pages()
    parseHtml()
    pass
