import json

import requests

api_url = "http://motoinfo.space:8081"


def get_motorcycles(top, **kwargs):
    params = {}
    if top:
        params['top'] = top

    data = {}
    data.update(dict(kwargs.items()))
    r = requests.post(f"{api_url}/motorcycles", params=params, data=json.dumps(data))
    if r.status_code == 200:
        return r.json()
    else:
        return []
