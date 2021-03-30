import json
import time

import requests


api_url = "http://localhost:8081"


def get_motorcycles(top, **kwargs):
    params = {}
    if top:
        params['top'] = top

    data = {}
    data.update(dict(kwargs.items()))
    print(data)
    print(json.dumps(data))
    while True:
        try:
            r = requests.post(f"{api_url}/motorcycles", params=params, data=json.dumps(data))
        except requests.exceptions.RequestException as e:
            pass
        # if r.status_code == 200:
        #     return r.json()
        # print(r.status_code)
        time.sleep(10)
