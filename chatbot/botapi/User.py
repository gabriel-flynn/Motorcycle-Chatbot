import requests

api_url = "http://localhost:8081"


def get_user():
    r = requests.get(f"{api_url}/user")
    if r.status_code == 200:
        return r.json()


def make_test_user():
    r = requests.post(f"{api_url}/user", data=json.dumps({'name': 'Gabriel'}))
    print(r.status_code)
    print(r.json())
