from urllib.parse import urlparse, urljoin
import re
import m3u8
import os


class M3u8File():
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
            playlist_resolution = 'x'.join(
                [str(value) for value in playlist.stream_info.resolution])
            if (playlist_resolution == resolution):
                return playlist

        return None

    def get_id(self):
        matches = re.search(
            r'\/video\/(?P<id>\w+)\/hls\/', self.url)
        return matches.group('id')

    def get_url_for(self, file_name):
        return urljoin(self.url, file_name)

    def get_segments_urls(self):
        segments = []
        for segment in self.content.segments:
            segments.append((segment.uri, self.get_url_for(segment.uri)))
        return segments

    def fetch_playlist(self, playlist, headers={}):
        playlist_content = M3u8File(
            self.get_url_for(playlist.uri)).fetch(headers)
        return playlist_content
