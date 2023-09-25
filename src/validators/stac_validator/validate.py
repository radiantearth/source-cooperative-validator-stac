import json
import os
from json.decoder import JSONDecodeError
from typing import Optional
from urllib.error import HTTPError, URLError

import click  # type: ignore
import jsonschema  # type: ignore
from jsonschema import RefResolver
from requests import exceptions  # type: ignore

from validators.stac_validator.stac_utilities import (
    get_stac_type,
    set_stac_schema_addr,
)

from utils.utilities import (
    fetch_and_parse_json,
    is_valid_url,
)
    
# Code configured to run 1.37x faster than using STACValidator pkg
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
    
    def load(self) -> None:
        # Load the STAC object to be validated for. Fetches the STAC content, type and version
        
        self.stac_content = fetch_and_parse_json(self.stac_file)
        self.stac_type = get_stac_type(self.stac_content).lower()
        self.version = self.stac_content["stac_version"]
    
    def core_validator(self, stac_type:str):
        """Validate the STAC item or collection against the appropriate JSON schema.

        Args:
            stac_type (str): The type of STAC object being validated (either "item" or "collection").

        Returns:
            None

        Raises:
            ValidationError: If the STAC object fails to validate against the JSON schema.

        The function first determines the appropriate JSON schema to use based on the STAC object's type and version.
        If the version is one of the specified versions (0.8.0, 0.9.0, 1.0.0, 1.0.0-beta.1, 1.0.0-beta.2, or 1.0.0-rc.2),
        it retrieves the schema from the appropriate URL using the `set_schema_addr` function.
        """
        stac_type = stac_type.lower()
        self.schema = set_stac_schema_addr(self.version, stac_type)
        if is_valid_url(self.schema):
            schema = fetch_and_parse_json(self.schema)
            jsonschema.validate(self.stac_content, schema)

    def extensions_validator(self, stac_type: str) -> dict:
        """Validate the STAC extensions according to their corresponding JSON schemas.

        Args:
            stac_type (str): The STAC object type ("ITEM" or "COLLECTION").

        Returns:
            dict: A dictionary containing validation results.

        Raises:
            JSONSchemaValidationError: If there is a validation error in the JSON schema.
            Exception: If there is an error in the STAC extension validation process.
        """
        message = self.create_message(stac_type, "extensions")
        valid = True

        if stac_type != "ITEM":
            self.core_validator(stac_type)
            message["schema"] = [self.schema]
            self.valid = valid
            return message

        try:
            if "stac_extensions" in self.stac_content:
                self.stac_content["stac_extensions"] = [ext.replace("proj", "projection") for ext in self.stac_content["stac_extensions"]]
                schemas = self.stac_content.get("stac_extensions", [])
                for extension in schemas:
                    if not (is_valid_url(extension) or extension.endswith(".json")):
                        extension = f"https://cdn.staclint.com/v{self.version}/extension/{extension}.json"
                    self.schema = extension
                    self.core_validator()
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
    
    def default_validator(self, stac_type: str) -> dict:
        """Validate the STAC catalog or item against the core schema and its extensions.

        Args:
            stac_type (str): The type of STAC object being validated. Must be either "catalog" or "item".

        Returns:
            A dictionary containing the results of the default validation, including whether the STAC object is valid,
            any validation errors encountered, and any links and assets that were validated.
        """
        message = self.create_message(stac_type, "default")
        message["schema"] = []
        self.core_validator(stac_type)
        core_schema = self.schema
        message["schema"].append(core_schema)
        stac_type = stac_type.upper()
        if stac_type == "ITEM":
            message = self.extensions_validator(stac_type)
            message["validation_method"] = "default"
            message["schema"].append(core_schema)
        
        return message 

    def recursive_validator(self, stac_type:str) -> bool:
        """Recursively validate a STAC JSON document against its JSON Schema.

        This method validates a STAC JSON document recursively against its JSON Schema by following its "child" and "item" links.
        It uses the `default_validator` and `fetch_and_parse_schema` functions to validate the current STAC document and retrieve the
        next one to be validated, respectively.

        Args:
            self: An instance of the STACValidator class.
            stac_type: A string representing the STAC object type to validate.

        Returns:
            A boolean indicating whether the validation was successful.

        Raises:
            jsonschema.exceptions.ValidationError: If the STAC document does not validate against its JSON Schema.

        """
        # TO DO: make stac_type lower throughout code
        if self.skip_val is False:
            self.schema = set_stac_schema_addr(self.version, stac_type.lower())

            message = self.create_message(stac_type, "recursive")
            message["valid_stac"] = False
            try:
                _ = self.default_validator(stac_type)

            except jsonschema.exceptions.ValidationError as e:
                if e.absolute_path:
                    err_msg = f"{e.message}. Error is in {' -> '.join([str(i) for i in e.absolute_path])}"
                else:
                    err_msg = f"{e.message} of the root of the STAC object"
                message.update(
                    self.create_err_msg("JSONSchemaValidationError", err_msg)
                )
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

            for link in self.stac_content["links"]:
                if link["rel"] == "child" or link["rel"] == "item":
                    address = link["href"]
                    if not is_valid_url(address):
                        x = str(base_url).split("/")
                        x.pop(-1)
                        st = x[0]
                        for i in range(len(x)):
                            if i > 0:
                                st = st + "/" + x[i]
                        self.stac_file = st + "/" + address
                    else:
                        self.stac_file = address

                    self.stac_content = fetch_and_parse_json(str(self.stac_file))
                    self.stac_content["stac_version"] = self.version
                    stac_type = get_stac_type(self.stac_content).lower()

                if link["rel"] == "child":
                    self.recursive_validator(stac_type)

                if link["rel"] == "item":
                    self.schema = set_stac_schema_addr(self.version, self.stac_type.lower())
                    message = self.create_message(stac_type, "recursive")
                    if self.version == "0.7.0":
                        schema = fetch_and_parse_json(self.schema)
                        # this next line prevents this: unknown url type: 'geojson.json' ??
                        schema["allOf"] = [{}]
                        jsonschema.validate(self.stac_content, schema)
                    else:
                        msg = self.default_validator(stac_type)
                        message["schema"] = msg["schema"]
                    message["valid_stac"] = True

                    if self.log != "":
                        self.message.append(message)
                    if (
                        not self.max_depth or self.max_depth < 5
                    ):  # TODO this should be configurable, correct?
                        self.message.append(message)
        return True

    def run(self) -> dict:
        """Runs the STAC validation process based on the input parameters.

        Returns:
            bool: True if the STAC is valid, False otherwise.

        Raises:
            URLError: If there is an error with the URL.
            JSONDecodeError: If there is an error decoding the JSON content.
            ValueError: If there is an invalid value.
            TypeError: If there is an invalid type.
            FileNotFoundError: If the file is not found.
            ConnectionError: If there is an error with the connection.
            exceptions.SSLError: If there is an SSL error.
            OSError: If there is an error with the operating system.
            jsonschema.exceptions.ValidationError: If the STAC content fails validation.
            KeyError: If the specified key is not found.
            HTTPError: If there is an error with the HTTP connection.
            Exception: If there is any other type of error.

        """
        message = {}
        try:
            if not self.stac_content:
                self.load()

            self.schema = set_stac_schema_addr(self.version, self.stac_type.lower())

            if self.core:
                message = self.create_message(self.stac_type, "core")
                self.core_validator(self.stac_type)
                message["schema"] = [self.schema]
                self.valid = True

            if self.extensions:
                message = self.extensions_validator(self.stac_type)

            elif self.recursive:
                self.valid = self.recursive_validator(self.stac_type)

            else:
                self.valid = True
                message = self.default_validator(self.stac_type)

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
            ConnectionError,
            exceptions.SSLError,
            OSError,
            KeyError,
            HTTPError,
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

        return self.valid