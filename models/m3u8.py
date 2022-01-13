from urllib.parse import urlparse, urljoin
from collections import namedtuple
import re
import m3u8
import os
import requests


FileUri = namedtuple("FileUri", "local_uri remote_url")


class M3u8Uri:
    def __init__(self, url):
        self.__url__ = url

    def id(self):
        matches = re.search(r"\/video\/(?P<id>\w+)\/hls\/", self.__url__)
        return matches.group("id")

    def url(self):
        return self.__url__

    def query(self):
        return urlparse(self.__url__).query

    def baseurl(self):
        return os.path.dirname(self.__url__)

    def basepath(self):
        return os.path.dirname(urlparse(self.__url__).path)[1:]

    def filename(self):
        return os.path.basename(urlparse(self.__url__).path)

    def join(self, basename, basepath=None):
        if basepath is None:
            return os.path.join(self.baseurl(), basename)
        return os.path.join(basepath, basename)

    def urljoin(self, path):
        return urljoin(self.baseurl(), path)

    def relative_uri(self, basename):
        return os.path.join(os.path.basename(self.basepath()), basename)


class M3u8Master:
    def __init__(self, uri: M3u8Uri):
        self.__uri__ = uri
        self.__m38u__ = None

    def fetch(self, headers):
        response = requests.get(self.__uri__.url(), headers=headers)
        response.raise_for_status()
        self.__m38u__ = m3u8.loads(response.content.decode("utf-8"))
        return self

    def playlists(self):
        return list(
            map(
                lambda playlist: FileUri(
                    local_uri=urlparse(playlist.uri).path,
                    remote_url=self.__uri__.join(basename=playlist.uri),
                ),
                self.__m38u__.playlists,
            )
        )

    def playlist(self, resolution) -> FileUri:
        if resolution is None:
            return None

        for playlist in self.__m38u__.playlists:
            playlist_resolution = "x".join(
                [str(value) for value in playlist.stream_info.resolution]
            )
            if playlist_resolution == resolution:
                return FileUri(
                    local_uri=urlparse(playlist.uri).path,
                    remote_url=self.__uri__.join(basename=playlist.uri),
                )

        return None


class M3u8Playlist:
    def __init__(self, uri: M3u8Uri):
        self.__uri__ = uri

    def fetch(self, headers):
        response = requests.get(self.__uri__.url(), headers=headers)
        response.raise_for_status()
        self.__m38u__ = m3u8.loads(response.content.decode("utf-8"))
        return self

    def segments(self):
        return list(
            map(
                lambda segment: FileUri(
                    local_uri=urlparse(self.__uri__.relative_uri(basename=segment.uri)).path,
                    remote_url=self.__uri__.urljoin(path=segment.uri),
                ),
                self.__m38u__.segments,
            )
        )

    def key(self):
        key_uri = self.__m38u__.segments[0].key.uri
        return FileUri(
            local_uri=urlparse(self.__uri__.relative_uri(basename=key_uri)).path,
            remote_url=self.__uri__.urljoin(path=key_uri),
        )


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
