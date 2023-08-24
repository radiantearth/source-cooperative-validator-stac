import click
import logging
import sys
import json
from validators.stac_validator import StacValidator
from validators.cog_validator import CogValidator

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug

@cli.command()
@click.argument("url")
@click.option('--validator', '-v', type=click.Choice(['stac', 'cog']), required=True)
def validate(url, validator):
    logging.info(f"Validating {validator.upper()} at {url}")
    
    if validator == 'stac':
        validator = StacValidator(url)
    elif validator == 'cog':
        validator = CogValidator(url)
    else:
        logging.error("Invalid validator type.")
        sys.exit(1)
    
    if validator.validate():
        logging.info(f"{validator} is valid!")
        sys.exit(0)
    else:
        logging.error(f"{validator} validation failed.")
        sys.exit(1)

@cli.command()
def info():
    print(json.dumps({
        "version": "1.0.0",
        "name": "STAC and COG Validator",
        "author": "Your Name"
    }, indent=4))
    sys.exit(0)

if __name__ == "__main__":
    FORMAT = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    cli(obj={})