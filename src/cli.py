import json
import sys
from typing import Any, Dict, List

import click  # type: ignore

from validators.stac_validator.stac_validator import StacValidate

def item_collection_summary(message: List[Dict[str, Any]]) -> None:
    """Prints a summary of the validation results for an item collection response.

    Args:
        message (List[Dict[str, Any]]): The validation results for the item collection.

    Returns:
        None
    """
    valid_count = 0
    for item in message:
        if "valid_stac" in item and item["valid_stac"] is True:
            valid_count = valid_count + 1
    click.secho()
    click.secho("--item-collection summary", bold=True)
    click.secho(f"items_validated: {len(message)}")
    click.secho(f"valid_items: {valid_count}")

@click.command()
@click.argument("stac_file")
@click.option(
    "--core", is_flag=True, help="Validate core stac object only without extensions."
)
@click.option("--extensions", is_flag=True, help="Validate extensions only.")
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Recursively validate all related stac objects.",
)
@click.option(
    "--max-depth",
    "-m",
    type=int,
    help="Maximum depth to traverse when recursing. Omit this argument to get full recursion. Ignored if `recursive == False`.",
)
@click.option(
    "-v", "--verbose", is_flag=True, help="Enables verbose output for recursive mode."
)
@click.option("--no_output", is_flag=True, help="Do not print output to console.")
@click.option(
    "--log_file",
    default="",
    help="Save full recursive output to log file (local filepath).",
)
def main(
    stac_file: str,
    recursive: bool,
    max_depth: int,
    core: bool,
    extensions: bool,
    verbose: bool,
    no_output: bool,
    log_file: str,
) -> None:
    """Main function for the `Source STAC Validator` command line tool. Validates a STAC file
    against the STAC specification and prints the validation results to the console as JSON.

    Args:
        stac_file (str): Path to the STAC file to be validated.
        recursive (bool): Whether to recursively validate all related STAC objects.
        max_depth (int): Maximum depth to traverse when recursing.
        core (bool): Whether to validate core STAC objects only.
        extensions (bool): Whether to validate extensions only.
        verbose (bool): Whether to enable verbose output for recursive mode.
        no_output (bool): Whether to print output to console.
        log_file (str): Path to a log file to save full recursive output.

    Returns:
        None

    Raises:
        SystemExit: Exits the program with a status code of 0 if the STAC file is valid,
            or 1 if it is invalid.
    """
    valid = True
    import time
    start  = time.time()
    stac = StacValidate(
        stac_file=stac_file,
        recursive=recursive,
        max_depth=max_depth,
        core=core,
        extensions=extensions,
        verbose=verbose,
        log=log_file,
    )
    valid = stac.run()
    end = time.time()
    message = stac.message
    diff = end - start
    print(f"Validation took: {round(diff, 2)} seconds...")
    if no_output is False:
        click.echo(json.dumps(message, indent=4))

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()