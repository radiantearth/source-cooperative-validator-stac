import functools
import json
from urllib.parse import urlparse

import requests  # type: ignore
import backoff

def backoff_hdlr(details):
    print ("Backing off {wait:0.1f} seconds after {tries} tries "
           "calling function {target} with args {args} and kwargs "
           "{kwargs}".format(**details))

def is_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def is_valid_url(url: str) -> bool:
    return urlparse(url).scheme in ["http", "https"]

@functools.lru_cache(maxsize=48)
@backoff.on_exception(backoff.expo,
                    (
                    requests.exceptions.ConnectionError,

                    ),
                    max_time=1800,
                    max_tries=10000,
                    on_backoff=backoff_hdlr)
def fetch_and_parse_json(input_path: str) -> dict:
    try:
        if is_url(input_path):
            resp = requests.get(input_path)
            resp.raise_for_status()
            data = resp.json()
        else:
            with open(input_path) as f:
                data = json.load(f)

        return data
    except (ValueError, requests.exceptions.RequestException) as e:
        raise e