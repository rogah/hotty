import os
import json

import click

from models.http_requests import HttpRequests


DEFAULT_OUTPUT = "~/.hotty/requests.json"


class Config:
    def __init__(self):
        pass


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group(invoke_without_command=True)
@pass_config
def cli(config):
    click.echo("Inside 'cli'")
    pass


@cli.command()
@click.option(
    "-f",
    "--file",
    type=click.File("r"),
    default=os.path.expanduser(DEFAULT_OUTPUT),
)
@pass_config
def fetch(config, file):
    click.echo(f"Inside 'load' {file}")

    try:
        data = json.load(file)
    except:
        click.echo("Error to load file.")
        raise click.Abort()

    requests = HttpRequests(requests=data)
    click.echo(f"Url: {requests.latest().url()}")


if __name__ == "__main__":
    cli()
