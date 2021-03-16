# Script to scrape motorcyclenews.com for reviews
import pickle
import re
import urllib.request
from os import mkdir, listdir
from os.path import isfile, join
from time import sleep
from urllib.error import HTTPError
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from web_scraping.Review import Review

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


def extract_model_and_year(model_and_year):
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


def extract_power_seat_and_weight(at_a_glance_items):
    power = None
    seat_category = None
    seat_height = None
    weight_category = None
    weight = None
    for item in at_a_glance_items:
        item = item.text
        item_arr = item.split(":")
        category = item_arr[0].strip()
        if category == "Power":
            power = re.findall(r":\s+([\d.]+)", item)[0]
        elif category == "Seat height":
            match = re.findall(r":\s+([\w]+)\s+\(([\d.]+)", item)[0]
            seat_category, seat_height = match[0], match[1]
        elif category == "Weight":
            match = re.findall(r":\s+([\w]+)\s+\(([\d.]+)", item)[0]
            weight_category, weight = match[0], match[1]

    return power, seat_height, weight


def traverse_ratings(ratings):
    rating_text = ""
    for rating in ratings:
        if not rating.img and rating.parent.name != 'blockquote':
            rating_text += rating.text + "\n"

    return rating_text.strip()


def extract_rating_and_review_section_information(html):
    ratings = html.select(".review__main-content .star-rating__text")  # Overall rating from 1-5
    rating_list = []
    for rating in ratings:
        rating_list.append(int(rating.text[1:2]))

    # Overall Rating
    rating_text = html.select(".review__main-content__section:nth-of-type(1)  p")  # Ride quality and brakes
    overall_rating_text = ""
    for rating in rating_text:
        if not rating.img and rating.parent.name != 'blockquote':
            overall_rating_text += rating.text + "\n"
    overall_rating_text.strip()

    # Ride quality & brakes
    rating_text = html.select(".review__main-content__section:nth-of-type(2)  p")  # Ride quality and brakes
    ride_quality_rating_text = traverse_ratings(rating_text)

    # Engine
    rating_text = html.select(".review__main-content__section:nth-of-type(4)  p")  # Ride quality and brakes
    engine_rating_text = traverse_ratings(rating_text)

    # Reliability & build quality
    rating_text = html.select(".review__main-content__section:nth-of-type(5)  p")  # Ride quality and brakes
    reliability_rating_text = traverse_ratings(rating_text)

    # Value vs rivals
    rating_text = html.select(".review__main-content__section:nth-of-type(6)  p")  # Ride quality and brakes
    value_rating_text = traverse_ratings(rating_text)

    # Equipment
    rating_text = html.select(".review__main-content__section:nth-of-type(8)  p")  # Ride quality and brakes
    equipment_rating_text = traverse_ratings(rating_text)

    return Review(overall_rating=rating_list[0], overall_rating_review_text=overall_rating_text,
                  ride_quality=rating_list[1], ride_quality_review_text=ride_quality_rating_text,
                  engine=rating_list[2], engine_review_text=engine_rating_text,
                  reliability=rating_list[3], reliability_review_text=reliability_rating_text,
                  value=rating_list[4], value_review_text=value_rating_text,
                  equipment=rating_list[5], equipment_review_text=equipment_rating_text)


def get_engine_type(html, engine_type_str):
    # Check engine type
    if re.search(r"(flat four)", engine_type_str):
        engine_type = "flat4"
    elif re.search(r"(transverse four)", engine_type_str):
        engine_type = "transverse4"
    elif re.search(r"(v4|vee 4)", engine_type_str):
        engine_type = "v4"
    elif re.search(
            r"(inline four|inlinefour|parallel 4cylinder|in line four|vfour|four cylinder|in line 4|inline 4|dohc four|inline, fourcylinder)",
            engine_type_str):
        engine_type = "i4"
    elif re.search(r"(electric|amp|brushless motor|magnet)", engine_type_str):
        engine_type = "electric"
    elif re.search(r"(ltwin)", engine_type_str):
        engine_type = "LTwin"
    elif re.search(r"(vtwin|v twin|vwin|2 cylinder 75 degree)", engine_type_str):
        engine_type = "vtwin"
    elif re.search(r"(flat twin|flattwin)", engine_type_str):
        engine_type = "flat2"
    elif re.search(r"(parallel twin|paralleltwin|in line twin|twincylinder|parallel 2cylinder|paralle twin|twin)",
                   engine_type_str):  # add twin
        engine_type = "i2"
    elif re.search(r"(threecylinder|three cylinder|triple|3cylinder|inline three)", engine_type_str):
        engine_type = "i3"
    elif re.search(r"(flat six|flat6|horizontallyopposed sixcylinder)", engine_type_str):
        engine_type = "flat6"
    elif re.search(r"(inline six|inline 6cylinder)", engine_type_str):
        engine_type = "i6"
    elif re.search(r"(boxer twin|boxertwin|twocylinder [\w\s]+boxer engine)", engine_type_str):
        engine_type = "box2"
    elif re.search(r"(single)", engine_type_str):
        engine_type = "i1"
    else:
        model_and_year = html.find("h1").text.upper().replace("REVIEW", "")
        print(model_and_year)
        engine_type = ""
        print(engine_type_str)
    return engine_type


def extract_engine_info_insurance_info_tank_range_and_power(html):
    sections = html.select(".review__facts-and-figures__table")

    # Section index 0 - Specs
    specs = [spec.text for spec in sections[0].select(".review__facts-and-figures__item__value")]
    engine_size = specs[0]
    engine_type = get_engine_type(html, specs[1].lower().replace("-", ""))

    # Section index 1 - Mpg, costs & insurance
    # mpg_cost_insurance = [item.text for item in sections[1].select(".review__facts-and-figures__item__value")]
    # mpg_uk_to_us_factor = 3.785411784/4.54609
    # print(mpg_cost_insurance[0])
    # mpg = float(mpg_cost_insurance[0].split(" ")[0]) * mpg_uk_to_us_factor
    # Section index 2 - Top speed & performance
    return engine_type


def parseHtml():
    path = f'{data_folder}/{mcn_folder}/{html_folder}'
    files = [f for f in listdir(path) if isfile(join(path, f))]

    engine_types = set()
    for file in files:
        html = BeautifulSoup(open(f'{path}/{file}'), features="html.parser")

        # # # Extract model and year

        # manufacturer, model, year_start, year_end = extract_model_and_year(model_and_year)
        #
        # # Extract information from "At a glance" section
        # at_a_glance_items = html.find_all("tr", class_="review__at-a-glance__item")
        # power, seat_height, weight = extract_power_seat_and_weight(at_a_glance_items)
        #
        # # Extract rating information
        # review = extract_rating_and_review_section_information(html)
        # # print(rating_text)

        engine_type = extract_engine_info_insurance_info_tank_range_and_power(html)
        engine_types.add(engine_type)
    print(engine_types)


if __name__ == "__main__":
    # uncomment to regenerate review or html pages
    # scrape_review_urls()
    # scrape_review_html_pages()
    parseHtml()
    pass
