import functools
import json
from urllib.parse import urlparse

import requests  # type: ignore

def is_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_valid_url(url: str) -> bool:
    return urlparse(url).scheme in ["http", "https"]

@functools.lru_cache(maxsize=48)
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