# Script to scrape motorcyclenews.com for reviews
import os
import pickle
import re
import urllib.request
from os import mkdir, listdir
from os.path import isfile, join
from time import sleep
from urllib.error import HTTPError
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from web_scraping import kbb, wikipedia
from web_scraping.Motorcycle import Motorcycle
from web_scraping.Review import Review
from web_scraping.model.Models import Motorcycle as MotorcycleModel
from web_scraping.model.Models import Review as ReviewModel
from dotenv import load_dotenv

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

    matches = re.findall(r"^([\w\-]+) ([\w\-\s./&+°]+) \(([\d]+)\s?-\s?([\w]+)\)", model_and_year)[0]

    manufacturer = ""
    model = ""
    year_start = 1800
    year_end = 0

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


def extract_rating_and_review_section_information(html, model):
    ratings = html.select(".review__main-content .star-rating__text")  # Overall rating from 1-5
    rating_list = []
    for rating in ratings:
        rating_list.append(int(rating.text[1:2]))

    if not rating_list:
        for i in range(6):
            rating_list.append(None)

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

    if model in {"HUSQVARNA 701 ENDURO (2015 - ON)", "HARLEY-DAVIDSON ROAD GLIDE SPECIAL (2015 - ON)",
                 "KAWASAKI Z650 (2017 - 2019)", "SUZUKI GSX-R1000R (2017 - ON)"}:
        rating_list.insert(1, None)
    elif model in {"SWM SIX DAYS 440 (2018 - ON)"}:
        rating_list.insert(2, None)
        rating_list.insert(5, None)
    elif model in {"HARLEY-DAVIDSON DELUXE (2018 - ON)"}:
        rating_list.insert(3, None)
    elif model in {"YAMAHA MT-10 SP (2017 - ON)"}:
        rating_list.insert(1, None)
        rating_list.insert(2, None)
    elif model in {"SUZUKI DL1050 V-STROM (2020 - ON)"}:
        rating_list.insert(4, None)
        rating_list.insert(5, None)
    elif model in {"TRIUMPH ROCKET 3 (2020-ON)", "HONDA CB1100RS (2017 - 2021)"}:
        rating_list.insert(5, None)
    elif model in {"YAMAHA MT-07 (2021 - ON)", "KAWASAKI Z650 (2020 - ON)"}:
        rating_list.insert(4, None)
    elif model in {"YAMAHA XMAX 400 (2018 - ON)"}:
        rating_list.insert(0, None)
        rating_list.insert(1, None)
        rating_list.insert(2, None)
        rating_list.insert(3, None)
        rating_list.insert(5, None)

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
        # print(model_and_year)
        engine_type = ""
        # print(engine_type_str)
    return engine_type


def extract_engine_info_insurance_info_tank_range_and_power(html):
    sections = html.select(".review__facts-and-figures__table")

    # Section index 0 - Specs
    specs = [spec.text for spec in sections[0].select(".review__facts-and-figures__item__value")]
    engine_size = specs[0][:-2] if len(specs[0]) > 0 else 0
    engine_type = get_engine_type(html, specs[1].lower().replace("-", ""))

    # Section index 1 - Mpg, costs & insurance
    mpg_cost_insurance = [item.text for item in sections[1].select(".review__facts-and-figures__item__value")]
    mpg = None
    if mpg_cost_insurance[0] != '-':
        mpg_uk_to_us_factor = 3.785411784 / 4.54609
        mpg = float(mpg_cost_insurance[0].split(" ")[0]) * mpg_uk_to_us_factor
    insurance_group = None
    if '-' not in mpg_cost_insurance[5]:
        insurance_group = int(mpg_cost_insurance[5].split(" ")[0])

    # Section index 2 - Top speed & performance
    power_and_tank_range = [item.text for item in sections[2].select(".review__facts-and-figures__item__value")]
    power = None
    if '-' not in power_and_tank_range[0]:
        power = int(power_and_tank_range[0].split(" ")[0])
    tank_range = None
    if '-' not in power_and_tank_range[4]:
        tank_range = power_and_tank_range[4].split(" ")[0]

    return engine_size, engine_type, mpg, insurance_group, power, tank_range


def parseHtml():
    path = f'{data_folder}/{mcn_folder}/{html_folder}'
    files = [f for f in listdir(path) if isfile(join(path, f))]

    moto_set = set()
    engine_types = set()
    category_set = set()
    for index, file in enumerate(files):
        html = BeautifulSoup(open(f'{path}/{file}'), features="html.parser")

        # Extract model and year
        model_and_year = html.find("h1").text.upper().replace("REVIEW", "").strip()
        print(f'\n\n{model_and_year}\t{index}')
        manufacturer, model, year_start, year_end = extract_model_and_year(model_and_year)

        # Extract information from "At a glance" section
        at_a_glance_items = html.find_all("tr", class_="review__at-a-glance__item")
        power, seat_height, weight = extract_power_seat_and_weight(at_a_glance_items)

        # Extract rating information
        review = extract_rating_and_review_section_information(html, model_and_year)
        # print(rating_text)

        engine_size, engine_type, mpg, insurance_group, power, tank_range = extract_engine_info_insurance_info_tank_range_and_power(
            html)
        engine_types.add(engine_type)
        print(engine_size)

        # Get the price using kbb
        price = kbb.get_price(f'{year_start} {manufacturer} {model}')
        price = 0 if price is None else price[1:].replace(",", "")
        category = wikipedia.get_category(f'{manufacturer} {model}')
        for c in category:
            category_set.add(c)
        category = " ".join(category)
        moto = Motorcycle(make=manufacturer, model=model, year_start=year_start, year_end=year_end, price=price,
                          category=category, engine_size=engine_size, engine_type=engine_type,
                          insurance_group=insurance_group, mpg=mpg, tank_range=tank_range, power=power,
                          seat_height=seat_height, weight=weight,
                          review=review)
        # print(moto)
        moto_set.add(moto)
    pickle.dump(moto_set, open(f'{data_folder}/{mcn_folder}/moto_set.pickle', 'wb'))
    print(engine_types)
    print(category_set)


def create_review_model(review):
    review_model = ReviewModel(overall_rating=review.overall_rating,
                               overall_rating_review_text=review.overall_rating_review_text,
                               ride_quality=review.ride_quality,
                               ride_quality_review_text=review.ride_quality_review_text, engine=review.engine,
                               engine_review_text=review.engine_review_text, reliability=review.reliability,
                               reliability_review_text=review.reliability_review_text, value=review.value,
                               value_review_text=review.value_review_text, equipment=review.equipment,
                               equipment_review_text=review.equipment_review_text)
    return review_model


def create_motorcycle_model(_moto):
    review = create_review_model(_moto.review)
    motorcycle = MotorcycleModel(make=_moto.make, model=_moto.model, year_start=_moto.year_start,
                                 year_end=_moto.year_end,
                                 price=_moto.price, category=_moto.category, engine_size=_moto.engine_size,
                                 engine_type=_moto.engine_type,
                                 insurance_group=_moto.insurance_group, mpg=_moto.mpg, tank_range=_moto.tank_range,
                                 power=_moto.power, seat_height=_moto.seat_height, weight=_moto.weight,
                                 review=review, review_id=review.id)
    return motorcycle


if __name__ == "__main__":
    # uncomment to regenerate review or html pages
    # scrape_review_urls()
    # scrape_review_html_pages()
    # parseHtml()
    load_dotenv()
    db_user = os.getenv('db_user')
    db_pass = os.getenv('db_pass')
    db_host = os.getenv('db_host')
    db_port = os.getenv('db_port')
    db_name = os.getenv('db_name')
    engine = create_engine(f"mysql://{db_user}:{db_pass}@{db_host}/{db_name}", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    moto_set = pickle.load(open(f'{data_folder}/{mcn_folder}/moto_set.pickle', 'rb'))
    for _moto in moto_set:
        moto = create_motorcycle_model(_moto)
        session.add(moto)
    session.commit()
    pass
