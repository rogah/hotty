import requests
import os

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
}


def get_headers(headers={}):
    return {
        **DEFAULT_HEADERS,
        **headers,
    }


def download_file(remote_uris, local_direcotry_uri, headers={}):
    filename, url = remote_uris
    local_filename = os.path.join(local_direcotry_uri, filename)

    print(f'Downloading {url}...')

    data = requests.get(url, headers=headers)
    print(f'Download status: {data.status_code}')
    with open(local_filename, 'wb')as file:
        file.write(data.content)

    print(f'Download complete for {local_filename}...')

    return local_filename
