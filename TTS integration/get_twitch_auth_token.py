from dotenv import load_dotenv

from cachetools import cached, TTLCache
import json
import os
import requests


@cached(cache=TTLCache(maxsize=2, ttl=14200))  # TODO fix caching
def get_auth_token():
    load_dotenv()

    payload = {
        'client_id': os.environ.get("TWITCH_CLIENT_ID"),
        'client_secret': os.environ.get("TWITCH_CLIENT_SECRET"),
        'code': os.environ.get("MY_AUTH_TWITCH_CODE"),
        'grant_type': 'authorization_code',
        'redirect_uri': 'http%3A%2F%2Flocalhost'
    }

    header = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    queryparams = ""

    for k, v in payload.items():
        queryparams = f"{queryparams}{k}={v}&"

    queryparams = queryparams[:-1]
    url = "https://id.twitch.tv/oauth2/token"
    print(url)
    r = requests.post(url, headers=header, data=queryparams)

    response = json.loads(r.text)
    print(r.text)
    access_token = response['access_token']

    return access_token
