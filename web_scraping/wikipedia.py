import pickle
from os import path, mkdir

data_folder = 'data'
wiki_folder = 'wiki'
cache_name = 'category_cache.pickle'
pickle_path = f'{data_folder}/{wiki_folder}/{cache_name}'

category_cache = {}
if path.exists(pickle_path):
    category_cache = pickle.load(open(pickle_path, 'rb'))

try:
    mkdir(f'{data_folder}/{wiki_folder}')
except FileExistsError:
    pass


def get_category(motorcycle):
    if motorcycle in category_cache:
        return category_cache[motorcycle]
    else:
        pass
        # query = f'{motorcycle} wikipedia'
        # print(query)
        # url = ''
        # for result in search(query, tld="com", lang="en", num=2, stop=2, pause=2):
        #     print(result)
        #     url = result
        #     break
        #
        # category = []
        # try:
        #     data = urllib.request.urlopen(url).read()
        #     soup = BeautifulSoup(data, features="html.parser")
        #     infos = soup.select(".infobox tr")
        #     for info in infos:
        #         info = info.text
        #         if "Class" in info:
        #             info = info.replace("Class", "")
        #             print(info)
        #             matches = re.findall(r"([a-zA-Z\-\s]+)", info)
        #             for match in matches:
        #                 match = match.strip()
        #                 if match:
        #                     category.append(match.strip())
        #             break
        # except:
        #     pass
        #
        # if category is []:
        #     print("ERROR: COULDN'T FIND A CLASS")
        # print(category)
        # category_cache[motorcycle] = category
        # pickle.dump(category_cache, open(f'{data_folder}/{wiki_folder}/{cache_name}', 'wb'))
