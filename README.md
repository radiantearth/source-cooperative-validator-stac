# Source Cooperative STAC Validator


Create a new conda environment and activate it using the following commands in the root of this repository:

`conda create --name source-stac-validator python=3.8`

`conda activate source-stac-validator`

Next, install the dependencies required for development:
```
make install-stac
```

## CLI

```
stac-validate --help
Usage: stac-validate [OPTIONS] STAC_FILE

  Main function for the `Source STAC Validator` command line tool. Validates a
  STAC file against the STAC specification and prints the validation results
  to the console as JSON.

  Args:     stac_file (str): Path to the STAC file to be validated.
  recursive (bool): Whether to recursively validate all related STAC objects.
  max_depth (int): Maximum depth to traverse when recursing.     core (bool):
  Whether to validate core STAC objects only.     extensions (bool): Whether
  to validate extensions only.     verbose (bool): Whether to enable verbose
  output for recursive mode.     no_output (bool): Whether to print output to
  console.     log_file (str): Path to a log file to save full recursive
  output.

  Returns:     None

  Raises:     SystemExit: Exits the program with a status code of 0 if the
  STAC file is valid,         or 1 if it is invalid.

Options:
  --core                   Validate core stac object only without extensions.
  --extensions             Validate extensions only.
  -r, --recursive          Recursively validate all related stac objects.
  -m, --max-depth INTEGER  Maximum depth to traverse when recursing. Omit this
                           argument to get full recursion. Ignored if
                           `recursive == False`.
  -v, --verbose            Enables verbose output for recursive mode.
  --no_output              Do not print output to console.
  --log_file TEXT          Save full recursive output to log file (local
                           filepath).
  --version                Show the version and exit.
  --help                   Show this message and exit.
  ```

## Example Usage
`stac-validate https://raw.githubusercontent.com/stac-utils/stac-validator/main/tests/test_data/v100/catalog.json --recursive`
```
Validation took: 17.33 seconds...
The STAC object is valid!
[
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/stac-utils/stac-validator/main/tests/test_data/v100/catalog.json",
        "schema": [
            "https://schemas.stacspec.org/v1.0.0/catalog-spec/json-schema/catalog.json"
        ],
        "valid_stac": true,
        "asset_type": "CATALOG",
        "validation_method": "recursive"
    },
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/stac-utils/stac-validator/main/tests/test_data/v100/./extensions-collection/collection.json",
        "schema": [
            "https://schemas.stacspec.org/v1.0.0/collection-spec/json-schema/collection.json"
        ],
        "valid_stac": true,
        "asset_type": "COLLECTION",
        "validation_method": "recursive"
    },
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/stac-utils/stac-validator/main/tests/test_data/v100/./extensions-collection/./proj-example/proj-example.json",
        "schema": [
            "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
            "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json"
        ],
        "valid_stac": true,
        "asset_type": "ITEM",
        "validation_method": "recursive"
    },
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/stac-utils/stac-validator/main/tests/test_data/v100/./collection-only/collection.json",
        "schema": [
            "https://schemas.stacspec.org/v1.0.0/collection-spec/json-schema/collection.json"
        ],
        "valid_stac": true,
        "asset_type": "COLLECTION",
        "validation_method": "recursive"
    },
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/stac-utils/stac-validator/main/tests/test_data/v100/./collection-only/collection-with-schemas.json",
        "schema": [
            "https://schemas.stacspec.org/v1.0.0/collection-spec/json-schema/collection.json"
        ],
        "valid_stac": true,
        "asset_type": "COLLECTION",
        "validation_method": "recursive"
    },
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/stac-utils/stac-validator/main/tests/test_data/v100/./collectionless-item.json",
        "schema": [
            "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
            "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json"
        ],
        "valid_stac": true,
        "asset_type": "ITEM",
        "validation_method": "recursive"
    }
]
```
### No Recursive Validation and No Output

`stac-validate https://raw.githubusercontent.com/stac-utils/stac-validator/main/tests/test_data/v100/catalog.json --no_output`
```
Validation took: 1.72 seconds...
The STAC object is valid!
```

## Building Container

`docker build -t source-stac-validator -f Dockerfile.stac .`

## Example
`docker run source-stac-validator https://raw.githubusercontent.com/stac-utils/stac-validator/main/tests/test_data/v100/catalog.json --no_output`
