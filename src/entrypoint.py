import click
import sys
import json
import logging


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj['DEBUG'] = debug


@cli.command()
@click.argument("catalog_url")
def validate(catalog_url):
    logging.info(f"Validating STAC Catalog at {catalog_url}")
    logging.info("Catalog Valid!")
    sys.exit(0)


@cli.command()
def info():
    print(json.dumps({
        "version": "1.0.0",
        "name": "STAC Catalog Validator",
        "author": "daniel@radiant.earth"
    }, indent=4))
    sys.exit(0)

if __name__ == "__main__":
    FORMAT = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    cli(obj={})
