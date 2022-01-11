import os
import json

import click
import requests

from models.http_request import HttpRequests
from models.m3u8 import M3u8Master, M3u8Playlist
from utils.string import to_snake_case


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
@click.option(
    "-r",
    "--resolution",
    default="1920x1080",
)
@click.option("-dir", "--download-directory", type=click.Path(), default=".")
@click.option("-d", "--download", is_flag=True, default=False)
@click.option("-alias", "--directory-alias", default="")
@click.option("-o", "--output", type=click.File("w"), default="-")
@pass_config
def fetch(
    config, file, resolution, download_directory, directory_alias, download, output
):
    click.echo(f"Inside 'load' {file}")

    try:
        data = json.load(file)
    except:
        click.echo(f"Error to load captured HTTP request file {file}.")
        raise click.Abort()

    try:
        requests = HttpRequests(data)
    except:
        click.echo("Error parsing .")
        raise click.Abort()

    http_request = requests.latest()

    try:
        m3u8_master = M3u8Master(http_request).fetch()
    except IOError as error:
        click.echo(
            click.style(
                f"Error fetching M3U8 master {http_request.url()} with error: {error}",
                fg="red",
            )
        )
        raise click.Abort()

    playlist_uri = m3u8_master.playlist(resolution)
    print(playlist_uri)

    try:
        m3u8_playlist = M3u8Playlist(http_request, playlist_uri).fetch()
    except IOError as error:
        click.echo(
            click.style(
                f"Error fetching M3U8 playlist {playlist_uri} with error: {error}",
                fg="red",
            )
        )
        raise click.Abort()

    segments_uris = m3u8_playlist.segments()
    print(segments_uris)

    if download:
        local_path = os.path.join(
            download_directory, to_snake_case(directory_alias), m3u8_master.id()
        )

        # if not os.path.exists(local_path):
        #     os.makedirs(local_path, exist_ok=True)

        # need to remove the query string for local naming

        local_master_filename = os.path.join(local_path, m3u8_master.filename())
        local_playlist_filename = os.path.join(local_path, m3u8_playlist.uri())
        local_key_filename = os.path.join(local_path, m3u8_playlist.key())

        print(local_path)
        print(local_master_filename)
        print(local_playlist_filename)
        print(local_key_filename)


if __name__ == "__main__":
    cli()
