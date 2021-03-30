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
    r = requests.post(f"{api_url}/motorcycles", params=params, data=json.dumps(data))
    if r.status_code == 200:
        return r.json()
    else:
        return []
