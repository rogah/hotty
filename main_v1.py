import os
from multiprocessing import Pool, cpu_count
from functools import partial

import click

from models.m3u8 import M3u8File
from models.cloudfront import CloudFront, QUERY_STRING_KEY_PAIR_ID, QUERY_STRING_POLICY, QUERY_STRING_SIGNATURE
from utils.downloader import download_file, get_headers
from utils.string import to_snake_case
from utils.url import parse_query_string


class Config:
    def __init__(self):
        self.m3u8_master = None
        self.cloudfront = None


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group(invoke_without_command=True)
@click.option('-o', '--output', type=click.File('w'), default=None)
@click.option('-i', '--cloudfront-id', default=None)
@click.option('-p', '--cloudfront-policy', default=None)
@click.option('-s', '--cloudfront-signature', default=None)
@click.argument('master-url')
@pass_config
def cli(config, output, cloudfront_id, cloudfront_policy, cloudfront_signature, master_url):
    query_parameters = parse_query_string(master_url)
    cloudfront_query_parameters = CloudFront.parse_query_parameters(
        query_parameters)

    config.cloudfront = CloudFront(
        key_parir_id=cloudfront_query_parameters[QUERY_STRING_KEY_PAIR_ID] or cloudfront_id,
        policy=cloudfront_query_parameters[QUERY_STRING_POLICY] or cloudfront_policy,
        signature=cloudfront_query_parameters[QUERY_STRING_SIGNATURE] or cloudfront_signature
    )

    config.m3u8_master = M3u8File(master_url).fetch(get_headers())

    if output is not None:
        click.echo(config.m3u8_master.get_data(), file=output)


@cli.command()
@click.option('-f', '--fetch', is_flag=True, default=False)
@click.option('-d', '--download', is_flag=True, default=False)
@click.option('-dir', '--download-directory', type=click.Path(), default=".")
@click.option('-alias', '--directory-alias', default='')
@click.option('-o', '--output', type=click.File('w'), default="-")
@click.argument('resolution')
@pass_config
def playlists(config, fetch, download, download_directory, directory_alias, output, resolution):
    if resolution is None:
        click.echo(click.style(
            f'A resolution must be specified (e.i. 1920x1080)', bg='red', fg='white'))
        click.echo(config.m3u8_master.get_data())
        return

    headers = get_headers(config.cloudfront.get_header())

    playlist = config.m3u8_master.serch_playlist_by_resolution(resolution)

    if playlist is None:
        click.echo(click.style(
            f'Playlist not found for resolution height of "{resolution}"', bg='red', fg='white'))
        click.echo(f'\nResolutions:')
        click.echo("\n".join(config.m3u8_master.get_resolutions()) + "\n")
        return
    else:
        click.echo(
            f'Playlist url: {config.m3u8_master.get_url_for(playlist.uri)}')

    if (fetch):
        m3u8_playlist = config.m3u8_master.fetch_playlist(
            playlist=playlist, headers=headers)
        click.echo(m3u8_playlist.get_data(), file=output)

        if (download):
            local_playlist_filename = os.path.join(
                download_directory,
                to_snake_case(directory_alias),
                config.m3u8_master.get_id(),
                playlist.uri
            )
            local_playlist_path = os.path.dirname(
                local_playlist_filename)
            if (not os.path.exists(local_playlist_filename)):
                os.makedirs(local_playlist_path, exist_ok=True)

            segments_key_filename = m3u8_playlist.content.segments[0].key.uri
            playlist_key_remote_uri = m3u8_playlist.get_url_for(
                segments_key_filename)

            pool = Pool(cpu_count())
            download_func = partial(
                download_file, local_direcotry_uri=local_playlist_path, headers=headers)
            pool.map(download_func, m3u8_playlist.get_segments_urls())
            pool.close()
            pool.join()

            download_file(remote_uris=(segments_key_filename, playlist_key_remote_uri),
                          local_direcotry_uri=local_playlist_path, headers=headers)

            download_file(remote_uris=(os.path.basename(playlist.uri), config.m3u8_master.get_url_for(playlist.uri)),
                          local_direcotry_uri=local_playlist_path, headers=headers)

            download_file(remote_uris=(config.m3u8_master.get_filename(), config.m3u8_master.url),
                          local_direcotry_uri=local_playlist_path, headers=headers)
