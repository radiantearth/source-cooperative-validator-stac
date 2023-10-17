import functools
import json
from urllib.parse import urlparse
from urllib3.exceptions import NewConnectionError

import requests  # type: ignore
import backoff

def backoff_hdlr(details):
    print ("Backing off {wait:0.1f} seconds after {tries} tries "
           "calling function {target} with args {args} and kwargs "
           "{kwargs}".format(**details))

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ReadTimeout,
                       requests.exceptions.ConnectTimeout,
                       requests.exceptions.ConnectionError,
                       NewConnectionError,
                       ),
                       max_time=1800, #try for 30 minutes
                      on_backoff=backoff_hdlr)
def is_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ReadTimeout,
                       requests.exceptions.ConnectTimeout,
                       requests.exceptions.ConnectionError,
                       NewConnectionError,
                       ),
                       max_time=1800, #try for 30 minutes
                      on_backoff=backoff_hdlr)
def is_valid_url(url: str) -> bool:
    return urlparse(url).scheme in ["http", "https"]

@functools.lru_cache(maxsize=48)
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ReadTimeout,
                       requests.exceptions.ConnectTimeout,
                       requests.exceptions.ConnectionError,
                       NewConnectionError,
                       ),
                       max_time=3600, #try for 60 minutes
                      on_backoff=backoff_hdlr)
def fetch_and_parse_json(input_path: str) -> dict:
    try:
        if is_url(input_path):
            resp = requests.get(input_path, timeout=3600)
            resp.raise_for_status()
            data = resp.json()
        else:
            with open(input_path) as f:
                data = json.load(f)

        return data
    except (ValueError, requests.exceptions.RequestException) as e:
        raise e

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ReadTimeout,
                       requests.exceptions.ConnectTimeout,
                       requests.exceptions.ConnectionError,
                       NewConnectionError,
                       ),
                       max_time=3600, #try for 60 minutes
                      on_backoff=backoff_hdlr)    
def fetch_and_parse_file(input_path: str) -> dict:
    """Fetches and parses a JSON file from a URL or local file.

    Given a URL or local file path to a JSON file, this function fetches the file,
    and parses its contents into a dictionary. If the input path is a valid URL, the
    function uses the requests library to download the file, otherwise it opens the
    local file with the json library.

    Args:
        input_path: A string representing the URL or local file path to the JSON file.

    Returns:
        A dictionary containing the parsed contents of the JSON file.

    Raises:
        ValueError: If the input is not a valid URL or local file path.
        requests.exceptions.RequestException: If there is an error while downloading the file.
    """
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