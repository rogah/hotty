from urllib.parse import urlparse, urljoin
import re
import m3u8
import os
import requests

from .http_request import HttpRequest


class M3u8Master(object):
    def __init__(self, http_request: HttpRequest):
        self.http_request = http_request
        self.content = None

    def fetch(self):
        reqsponse = requests.get(
            self.http_request.url(), headers=self.http_request.headers()
        )
        reqsponse.raise_for_status()

        self.content = reqsponse.content.decode("utf-8")

        return self

    def id(self):
        matches = re.search(r"\/video\/(?P<id>\w+)\/hls\/", self.http_request.url())
        return matches.group("id")

    def filename(self):
        return os.path.basename(urlparse(self.http_request.url()).path)

    def playlists(self):
        m3u8_file = m3u8.loads(self.content)
        return list(
            map(
                lambda playlist: playlist.uri,
                m3u8_file.playlists,
            )
        )

    def playlist(self, resolution):
        if resolution is None:
            return None

        m3u8_file = m3u8.loads(self.content)

        for playlist in m3u8_file.playlists:
            playlist_resolution = "x".join(
                [str(value) for value in playlist.stream_info.resolution]
            )
            if playlist_resolution == resolution:
                return playlist.uri

        return None


class M3u8Playlist(object):
    def __init__(self, http_request: HttpRequest, playlist_uri: str):
        self.http_request = http_request
        self.playlist_uri = playlist_uri
        self.content = None

    def fetch(self):
        url = urljoin(self.http_request.url(), self.playlist_uri)
        reqsponse = requests.get(url, headers=self.http_request.headers())
        reqsponse.raise_for_status()

        self.content = reqsponse.content.decode("utf-8")

        return self

    def uri(self):
        return self.playlist_uri

    def filename(self):
        return os.path.basename(urlparse(self.playlist_uri).path)

    def segments(self):
        m3u8_file = m3u8.loads(self.content)
        return list(
            map(
                lambda segment: (
                    urljoin(self.playlist_uri, segment.uri),
                    urljoin(
                        urljoin(self.http_request.url(), self.playlist_uri), segment.uri
                    ),
                ),
                m3u8_file.segments,
            )
        )

    def key(self):
        m3u8_file = m3u8.loads(self.content)
        return urljoin(self.playlist_uri, m3u8_file.segments[0].key.uri)


class M3u8File:
    def __init__(self, url):
        self.url = url
        self.content = None

    def fetch(self, headers={}):
        self.content = m3u8.load(uri=self.url, headers=headers)
        return self

    def get_filename(self):
        return os.path.basename(urlparse(self.url).path)

    def get_data(self):
        return self.content.dumps()

    def get_playlists(self):
        return self.content.playlists

    def get_resolutions(self):
        def format_resolution(playlist):
            width, height = playlist.stream_info.resolution
            return f"{width}x{height}"

        return list(map(format_resolution, self.content.playlists))

    def serch_playlist_by_resolution(self, resolution):
        if resolution is None:
            return None

        for playlist in self.get_playlists():
            playlist_resolution = "x".join(
                [str(value) for value in playlist.stream_info.resolution]
            )
            if playlist_resolution == resolution:
                return playlist

        return None

    def get_id(self):
        matches = re.search(r"\/video\/(?P<id>\w+)\/hls\/", self.url)
        return matches.group("id")

    def get_url_for(self, file_name):
        return urljoin(self.url, file_name)

    def get_segments_urls(self):
        segments = []
        for segment in self.content.segments:
            segments.append((segment.uri, self.get_url_for(segment.uri)))
        return segments

    def fetch_playlist(self, playlist, headers={}):
        playlist_content = M3u8File(self.get_url_for(playlist.uri)).fetch(headers)
        return playlist_content
