import pickle
import re
import urllib.request
from os import path, mkdir

from googlesearch import search
from bs4 import BeautifulSoup

# https://www.kbb.com/motorcycles/suzuki/sv650/2006/?pricetype=retail

data_folder = 'data'
kbb_folder = 'kbb'
cache_name = 'price_cache.pickle'
pickle_path = f'{data_folder}/{kbb_folder}/{cache_name}'

price_cache = {}
if path.exists(pickle_path):
    price_cache = pickle.load(open(pickle_path, 'rb'))

try:
    mkdir(f'{data_folder}/{kbb_folder}')
except FileExistsError:
    pass


def get_price(motorcycle):
    if motorcycle in price_cache:
        return price_cache[motorcycle]
    else:
        pass
        # query = f'{motorcycle} kbb'
        # url = ''
        # for result in search(query, tld="com", lang="en", num=2, stop=2, pause=2):
        #     # print(f'{motorcycle}')
        #     # print(result)
        #     try:
        #         url = re.findall(r'(https://www\.kbb\.com/motorcycles/[\w-]+/[\w-]+/[\w]+/)', result)[0] + '?pricetype=retail'
        #         print(url)
        #     except:
        #         print(f'DO MANUAL: {motorcycle}')
        #         return
        #     break
        #
        # data = urllib.request.urlopen(url).read()
        # soup = BeautifulSoup(data, features="html.parser")
        # price = soup.select(".css-1f439jp")[0].text
        # if len(price) < 3:
        #     print(f'ERROR FOR {motorcycle} - price was {price}')
        # price_cache[motorcycle] = price
        # pickle.dump(price_cache, open(f'{data_folder}/{kbb_folder}/{cache_name}', 'wb'))
