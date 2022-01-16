import os
import json
from multiprocessing import Pool, cpu_count
from functools import partial

import click

from models.http_request import HttpRequests
from models.m3u8 import M3u8Uri, M3u8Master, M3u8Playlist
from utils.string import to_snake_case
from utils.downloader import download_file


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
    "-f", "--file", type=click.File("r"), default=os.path.expanduser(DEFAULT_OUTPUT)
)
@click.option("-r", "--resolution", default="1920x1080")
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

    http_request = HttpRequests(data).latest()
    m3u8_master_uri = M3u8Uri(http_request.url())

    try:
        m3u8_master = M3u8Master(m3u8_master_uri).fetch(http_request.headers())
    except IOError as error:
        click.echo(
            click.style(
                f"Error fetching M3U8 master {http_request.url()} with error: {error}",
                fg="red",
            )
        )
        raise click.Abort()

    playlist_uris = m3u8_master.playlist(resolution)
    m3u8_playlist_uri = M3u8Uri(playlist_uris.remote_url)

    try:
        m3u8_playlist = M3u8Playlist(m3u8_playlist_uri).fetch(http_request.headers())
    except IOError as error:
        click.echo(
            click.style(
                f"Error fetching M3U8 playlist {playlist_uris} with error: {error}",
                fg="red",
            )
        )
        raise click.Abort()

    playlist_segments_uris = m3u8_playlist.segments()
    playlist_key_uris = m3u8_playlist.key()
    master_uris = m3u8_master.master_uris()

    files_uris = [master_uris, playlist_uris, playlist_key_uris] + playlist_segments_uris

    if download:
        local_basepath = os.path.join(
            download_directory, to_snake_case(directory_alias), m3u8_master_uri.id()
        )

        local_playlist_basepath = os.path.join(
            local_basepath, os.path.basename(m3u8_playlist_uri.basepath())
        )

        if not os.path.exists(local_playlist_basepath):
            os.makedirs(local_playlist_basepath, exist_ok=True)

        pool = Pool(cpu_count())
        download_func = partial(
            download_file, local_direcotry_uri=local_basepath, headers=http_request.headers())
        pool.map(download_func, files_uris)
        pool.close()
        pool.join()


if __name__ == "__main__":
    cli()
