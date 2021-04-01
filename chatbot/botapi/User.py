import json

import requests

api_url = "http://localhost:8081"


def get_user():
    r = requests.get(f"{api_url}/user")
    if r.status_code == 200:
        return r.json()


def create_user_and_get_user_location(is_new_user, name):
    if is_new_user:
        requests.delete(f"{api_url}/user")
        r = requests.post(f"{api_url}/user", data=json.dumps({'name': name}))
        return r.json()
    else:
        return get_user()


def update_location(location):
    r = requests.patch(f"{api_url}/user/location", data=json.dumps({"location_string": location}))
    return r.json()


def get_closest_track_travel_time():
    r = requests.get(f"{api_url}/user/track", params={"closest": "true"})
    return r.json()


def make_test_user():
    r = requests.post(f"{api_url}/user", data=json.dumps({'name': 'Gabriel'}))
    print(r.status_code)
    print(r.json())


def save_motorcycle_recommendations(motorcycles):
    requests.post(f"{api_url}/user/motorcycles", data=json.dumps(motorcycles))
