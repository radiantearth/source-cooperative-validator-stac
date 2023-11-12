import json
import time   
import sys
import os
from json.decoder import JSONDecodeError
from typing import Optional
from urllib.error import HTTPError, URLError

import click  # type: ignore
import jsonschema  # type: ignore
from jsonschema import RefResolver
from requests import exceptions  # type: ignore
import requests

from validators.stac_validator.stac_utilities import (
    get_stac_type,
    set_stac_schema_addr,
)

import asyncio
import aiohttp

import json
import time
import os
from json.decoder import JSONDecodeError
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib3.exceptions import NewConnectionError

import click  # type: ignore
import jsonschema  # type: ignore
from jsonschema import RefResolver
from requests import exceptions  # type: ignore
import backoff

import functools
import json
import ssl
from urllib.parse import urlparse
from urllib.request import urlopen
import requests

import concurrent.futures

def is_valid_url(url: str) -> bool:
    """Checks if a given string is a valid URL.

    Args:
        url: A string to check for validity as a URL.

    Returns:
        A boolean value indicating whether the input string is a valid URL.
    """
    return urlparse(url).scheme in ["http", "https"]

def is_url(url: str) -> bool:
    """Checks whether the input string is a valid URL.

    Args:
        url (str): The string to check.

    Returns:
        bool: True if the input string is a valid URL, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
'''
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ReadTimeout,
                       requests.exceptions.ConnectTimeout,
                       requests.exceptions.ConnectionError,
                       NewConnectionError,
                       ConnectionResetError,
                       ),
                       max_time=3600, #try for 30 minutes
                    )    
async def fetch_and_parse_json_async(session, url: str) -> dict:
    async with session.get(url, timeout=3600) as response:
        response.raise_for_status()
        return await response.json(content_type=response.content_type)

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ReadTimeout,
                       requests.exceptions.ConnectTimeout,
                       requests.exceptions.ConnectionError,
                       NewConnectionError,
                       ConnectionResetError,
                       ),
                       max_time=3600, #try for 30 minutes
                      )
async def fetch_and_parse_json(input_path: str) -> dict:
    try:
        if is_url(input_path):
            async with aiohttp.ClientSession() as session:
                return await fetch_and_parse_json_async(session, input_path)
        else:
            with open(input_path) as f:
                return json.load(f)
    except (ValueError, requests.exceptions.RequestException) as e:
        raise e
'''

class StacValidate:
    def __init__(
        self,
        stac_file: str = None,
        recursive: bool = False,
        
        max_depth: int = None,
        custom: str = "",
        core: bool = False,
        extensions: bool = False,
        verbose: bool = False,
        log: str = "",
    ):
        self.stac_file = stac_file
        self.message = []
        self.semaphore = asyncio.Semaphore()
        self.items_validated = 0
        self.start_time = time.time()
        self.schema = custom
        self.recursive = recursive
        self.max_depth = max_depth
        self.core = core
        self.extensions = extensions
        self.stac_content = {}
        self.version = ""
        self.depth = 0
        self.skip_val = False
        self.verbose = verbose
        self.valid = False
        self.log = log

    def create_err_msg(self, err_type: str, err_msg: str) -> dict:
        self.valid = False
        return {
            "version": self.version,
            "path": self.stac_file,
            "schema": [self.schema],
            "valid_stac": False,
            "error_type": err_type,
            "error_message": err_msg,
        }

    def create_links_message(self):
        format_valid = []
        format_invalid = []
        request_valid = []
        request_invalid = []
        return {
            "format_valid": format_valid,
            "format_invalid": format_invalid,
            "request_valid": request_valid,
            "request_invalid": request_invalid,
        }

    def create_message(self, stac_type: str, val_type: str) -> dict:
        return {
            "version": self.version,
            "path": self.stac_file,
            "schema": [self.schema],
            "valid_stac": False,
            "asset_type": stac_type.upper(),
            "validation_method": val_type,
        }
    
    async def fetch_and_parse_json_async(self, session, url: str) -> dict:
        async with session.get(url, timeout=3600) as response:
            response.raise_for_status()
            return await response.json(content_type=response.content_type)
       
    async def load(self, session):
        async with self.semaphore:
            self.stac_content = await self.fetch_and_parse_json_async(session, self.stac_file)
            self.stac_type = get_stac_type(self.stac_content).lower()
            self.version = self.stac_content["stac_version"]
    
    # Modify the core_validator_async method
    async def core_validator_async(self, stac_type: str, session) -> None:
        stac_type = stac_type.lower()
        self.schema = set_stac_schema_addr(self.version, stac_type)
        if is_valid_url(self.schema):
            schema = await self.fetch_and_parse_json_async(session, self.schema)
            jsonschema.validate(self.stac_content, schema)

    # Modify the extensions_validator_async method
    async def extensions_validator_async(self, stac_type: str, session) -> dict:
        message = self.create_message(stac_type, "extensions")
        valid = True

        if stac_type != "ITEM":
            await self.core_validator_async(stac_type, session)
            message["schema"] = [self.schema]
            self.valid = valid
            return message

        try:
            if "stac_extensions" in self.stac_content:
                self.stac_content["stac_extensions"] = [ext.replace("proj", "projection") for ext in
                                                        self.stac_content["stac_extensions"]]
                schemas = self.stac_content.get("stac_extensions", [])
                for extension in schemas:
                    if not (is_valid_url(extension) or extension.endswith(".json")):
                        extension = f"https://cdn.staclint.com/v{self.version}/extension/{extension}.json"
                    self.schema = extension
                    await self.core_validator_async(stac_type, session)
                    message["schema"].append(extension)
        except jsonschema.exceptions.ValidationError as e:
            valid = False
            err_msg = f"{e.message}. Error is in {' -> '.join([str(i) for i in e.absolute_path])}"
            message = self.create_err_msg("JSONSchemaValidationError", err_msg)
        except Exception as e:
            valid = False
            err_msg = f"{e}. Error in Extensions."
            message = self.create_err_msg("Exception", err_msg)

        self.valid = valid
        return message

    async def default_validator_async(self, stac_type: str, session) -> dict:
        message = self.create_message(stac_type, "default")
        message["schema"] = []
        await self.core_validator_async(stac_type, session)  # Pass the session here
        core_schema = self.schema
        message["schema"].append(core_schema)
        stac_type = stac_type.upper()
        if stac_type == "ITEM":
            message = await self.extensions_validator_async(stac_type, session)  # Pass the session here
            message["validation_method"] = "default"
            message["schema"].append(core_schema)

        return message
    
    
    async def process_link(self, sem, session, link, base_url, version):
        async with sem:
            address = link["href"]
            if not is_valid_url(address):
                x = str(base_url).split("/")
                x.pop(-1)
                st = x[0]
                for i in range(len(x)):
                    if i > 0:
                        st = st + "/" + x[i]
                stac_file = st + "/" + address
            else:
                stac_file = address

            try:
                self.stac_file = stac_file
                self.stac_content = await self.fetch_and_parse_json_async(session, stac_file)
                self.stac_content["stac_version"] = version
                local_stac_type = get_stac_type(self.stac_content).lower()

                if link["rel"] == "child":
                    await self.recursive_validator_async(local_stac_type, session)

                if link["rel"] == "item":
                    schema = set_stac_schema_addr(version, local_stac_type)
                    msg = self.create_message(local_stac_type, "recursive")
                    if version == "0.7.0":
                        schema_content = await self.fetch_and_parse_json_async(session, schema)
                        schema_content["allOf"] = [{}]
                        jsonschema.validate(self.stac_content, schema_content)
                    else:
                        await self.default_validator_async(local_stac_type, session)
                        msg["schema"] = [self.schema]
                    msg["valid_stac"] = True

                    if self.log != "":
                        self.message.append(msg)
                    if not self.max_depth or self.max_depth < 5:
                        self.message.append(msg)

                    # Print progress
                    self.items_validated += 1
                    elapsed_time = time.time() - self.start_time
                    items_per_second = self.items_validated / elapsed_time
                    click.echo(
                        f"\rValidated STAC items: {self.items_validated} | Items/sec: {items_per_second:.2f}", nl=False)

            except jsonschema.exceptions.ValidationError as e:
                if e.absolute_path:
                    err_msg = f"{e.message}. Error is in {' -> '.join([str(i) for i in e.absolute_path])}"
                else:
                    err_msg = f"{e.message} of the root of the STAC object"
                msg = self.create_err_msg("JSONSchemaValidationError", err_msg)
                self.message.append(msg)
                if self.verbose is True:
                    click.echo(json.dumps(msg, indent=4))

    async def recursive_validator_async(self,stac_type:str, session) -> bool:
        if self.skip_val is False:
            self.schema = set_stac_schema_addr(self.version, stac_type.lower())
            message = self.create_message(stac_type, "recursive")
            message["valid_stac"] = False

            try:
                await self.default_validator_async(stac_type, session)
            except jsonschema.exceptions.ValidationError as e:
                if e.absolute_path:
                    err_msg = f"{e.message}. Error is in {' -> '.join([str(i) for i in e.absolute_path])}"
                else:
                    err_msg = f"{e.message} of the root of the STAC object"
                message.update(self.create_err_msg("JSONSchemaValidationError", err_msg))
                self.message.append(message)
                if self.verbose is True:
                    click.echo(json.dumps(message, indent=4))
                return False

            message["valid_stac"] = True
            self.message.append(message)
            if self.verbose:
                click.echo(json.dumps(message, indent=4))
            self.depth += 1
            if self.max_depth and self.depth >= self.max_depth:
                self.skip_val = True
            base_url = self.stac_file

            # Use a list to store the tasks and then await them individually
            tasks = []
            #sem = asyncio.Semaphore()
            async with aiohttp.ClientSession() as session:
                for link in self.stac_content["links"]:
                    if link["rel"] in {"child", "item"}:
                        task = asyncio.ensure_future(self.process_link(sem, session, link, base_url, self.version))
                        tasks.append(task)

                await asyncio.gather(*tasks)

            #sys.stdout.write("\n")  # To move to the next line after validation completes

        return True
            

        '''
        tasks = [process_link(link, base_url, self.version) for link in
                self.stac_content["links"] if link["rel"] in {"child", "item"}]
        await asyncio.gather(*tasks)
        '''

        return True
        '''
        # Use a list to store the tasks and then await them individually
        tasks = [process_link(link, base_url, self.version) for link in self.stac_content["links"] if link["rel"] in {"child", "item"}]
        for task in tasks:
            await task
        
            # Use a list to store the tasks and then await them individually
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(process_link, link, base_url, self.version) for link in self.stac_content["links"] if link["rel"] in {"child", "item"}]

            # Wait for all tasks to complete
            concurrent.futures.wait(futures)
        '''

    
    async def run_async(self, session) -> dict:
        message = {}
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=1000)) as session:
            try:
                if not self.stac_content:
                    await self.load(session)

                self.schema = set_stac_schema_addr(self.version, self.stac_type.lower())

                if self.core:
                    message = self.create_message(self.stac_type, "core")
                    await self.core_validator_async(session, self.stac_type)
                    message["schema"] = [self.schema]
                    self.valid = True

                if self.extensions:
                    message = await self.extensions_validator_async(self.stac_type, session)

                elif self.recursive:
                    self.valid = await self.recursive_validator_async(self.stac_type, session)

                else:
                    self.valid = True
                    message = await self.default_validator_async(self.stac_type, session)

            except jsonschema.exceptions.ValidationError as e:
                if e.absolute_path:
                    err_msg = f"{e.message}. Error is in {' -> '.join([str(i) for i in e.absolute_path])} "
                else:
                    err_msg = f"{e.message} of the root of the STAC object"
                message.update(self.create_err_msg("JSONSchemaValidationError", err_msg))

            except (
                    URLError,
                    JSONDecodeError,
                    ValueError,
                    TypeError,
                    FileNotFoundError,
                    aiohttp.ClientConnectionError,
                    aiohttp.ClientSSLError,
                    OSError,
                    KeyError,
                    aiohttp.ClientResponseError,
            ) as e:
                message.update(self.create_err_msg(type(e).__name__, str(e)))

            except Exception as e:
                message.update(self.create_err_msg("Exception", str(e)))

            if message:
                message["valid_stac"] = self.valid
                self.message.append(message)

            if self.log != "":
                with open(self.log, "w") as f:
                    f.write(json.dumps(self.message, indent=4))

            return self

'''
import time   
start = time.time() 
with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=1000)) as session:
    stac = StacValidate(
                stac_file='https://raw.githubusercontent.com/stac-utils/stac-validator/main/tests/test_data/v100/catalog.json',
                recursive=True,
            )
    stac.run_async(session)

print(stac.message)
print(time.time())

'''
start = time.time()

async def main():
    async with aiohttp.ClientSession() as session:
        stac = StacValidate(
            stac_file='https://storage.googleapis.com/cfo-public/catalog.json',
            recursive=True,
        )

        # Run the asynchronous validation
        await stac.run_async(session)
        
        print(json.dumps(stac.message, indent=4))
        print(stac.valid)

asyncio.run(main())

end = time.time()
diff = end - start
print(diff)


'''
async def main2():
    # Create an instance of StacValidate
    stac = StacValidate(
        stac_file='https://radarstac.s3.amazonaws.com/stac/catalog.json',
        recursive=True,
    )

    # Run the asynchronous validation
    await stac.run_async()
    print(stac.valid)
    #print(json.dumps(stac.message, indent=4))

    # You can do something with the result if needed
    #print(f"STAC validation result: {result}")

asyncio.run(main2())
end = time.time()
diff = end - start 
print(diff)
'''
