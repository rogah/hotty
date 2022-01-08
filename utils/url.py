from urllib.parse import urlparse, parse_qsl


def parse_query_string(url):
    parsed_url = urlparse(url)
    return parse_qsl(parsed_url.query)
