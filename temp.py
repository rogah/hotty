from utils.downloader import download_file, get_headers
from urllib.parse import urlparse, urlunparse, parse_qsl, urljoin, ParseResult
from models.m3u8 import M3u8File
import requests
import os
from pathlib import Path
import m3u8


def strip_scheme_and_host(parsed_url):
    return ParseResult('', '', *parsed_url[2:]).geturl()


master_url = 'https://vod-akm.play.hotmart.com/video/GZWWXYEzZA/hls/master-t-1636104637000.m3u8?hdnts=st%3D1640861708%7Eexp%3D1640862208%7Ehmac%3D2b8379072f6c2f0e9365dc8161d87e02260689c18c6aa80a3417a1a963e2f5b3'

# master_url = 'https://vod-akm.play.hotmart.com/video/GZWWXYEzZA/hls/1080/1080.m3u8?hdntl=exp=1640948328~acl=/*~data=hdntl~hmac=ca3e587af801444b1a68d1f5e33ffb45ecf22ba9e99c77fcad492d97ea72c1f3'

master_parsed_url = urlparse(master_url)
master_url_path = master_parsed_url.path
master_url_query = master_parsed_url.query

filename = os.path.basename(master_url_path)

local_directory = os.path.expanduser('~/Downloads/red')
local_file_uri = os.path.join(local_directory, filename)


headers = get_headers({
    "method": "GET",
    "scheme": "https",
    "authority": "vod-akm.play.hotmart.com",
    "path": strip_scheme_and_host(parsed_url=master_parsed_url),
    "Accept": "*/*",
    "Connection": "Keep-Alive",
    "Host": "vod-akm.play.hotmart.com",
    "Accept-Language": "en-au",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
    "Referer": "https://cf-embed.play.hotmart.com/",
    "Accept-Encoding": "gzip",
    "X-Playback-Session-Id": "FB57F302-1A6D-4AAE-ADC0-B2537A20FC89",
    "Cookie": 'hmLangCookie=en; _fbp=fb.1.1638349378828.1158453577; _hjAbsoluteSessionInProgress=0; _hjSessionUser_1022482=eyJpZCI6ImE1ZGJjOWE3LTQ5YjgtNTVkNy1hMmQ2LTE3YTA5YzIxZTY1YSIsImNyZWF0ZWQiOjE2MzgzNDk2MDQyNjYsImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_1022482=eyJpZCI6IjJlY2FjMTM3LWU3NzctNGM1Mi1hYjZmLWMzZWM5MWQ0YTUxZiIsImNyZWF0ZWQiOjE2NDA4NjE2NjI5Njh9; hotid=eyJjaWQiOiIxNjM4MzQ5Mzg1NjkyNDgyNjQ2MTk2NTc2MzEyNjAwIiwiYmlkIjoiMTYzODM0OTM4NTY5MjQ4MjY0NjE5NjU3NjMxMjYwMCIsInNpZCI6ImUyNmNjZWM5OGI4MTQ0NjM4OGQzOWVlNGViYWUwMmIxIn0=; _ga=GA1.2.1922062359.1638349379; _gid=GA1.2.1102082440.1640861663; _gat_gtag_UA_1708309_17=1; hmVlcIntegration=H4sIAAAAAAAAAI1R2W6zOBR%252Bov4yBkq5pAFSU2wXMIu5qQKkAbOmkBB4%252BnFGI81czoWlo7N8m8%252BbVxfHsqGNF8U7UkiDZjSEenlAr6idsuTgmX%252FOm6eUMNkyqNdFGj%252BXtwJWXdl3d38obxy6W9W78%252BloWjlU6lO6yp650N2tc2ZBLgLgM2vL7XYhNtZxozRctJqfxpDYpOMpf%252BAUQRw9yYko1PcOialAgydnQeMfPFVygTzyKlmPhRosVUa6spEiBVbIjjXCkE4V756%252F0empCzmkLodcmqvvdJ8fhLU3zFroCwfSSJM3y%252F%252FzoEpM6f2Umuq%252FO28GZvxBbAtgwVUirBXby7vUBMrnPHUMCryvxLkYQRZOVf9mhLFmJAlxKHR7DrFCGdp8Fu%252BUxTKT9z4%252FAJ0Ir5c5qTm7QMoucoZUzGYD21K%252FCFbpU%252FKVQPJuFFSnGEw4TRKvSsGDJCMIuromsbYmrB7xkaDT3jWl%252FZ98dgdiJnFEvFIbSc2WIbORD6%252BUzf%252FUs4GatcmzekVi%252FJuXSk3YLoHMvq6yUObvTdWx68oNvaabx2LHjSLwcDMlYWGCnv8lCqisMou2UFGTRWtzGsJJ4jWSc%252BPiXRBWLrx3dt4AwFOv81mrUtmjzGsJi3W8Jz22ne2phcPHlKc6yGDXPjFyljf5MREcokV6U%252BgBACrv%252FRTtfLcWvLuCM1LLe4XvbocG8Ofz%252FPJBtwnSxB8RXx9BbU2z%252BS3qQ7WY99vHbdSXFr8PZ2KH7sXL0utEIfGsWlQGnZ0iFTvJbPN6DIo9cFaW3WZFwaeoV8RVqvxatLmMr%252FVlyHhrIWMf4vb7cpl%252BVTiOPGivvE9It29mitDhMwKX%252Fq3ruy%252BdvdWP8%252BAGM7gWPnAc2ph%252BUt1B%252FqFyHgg8hfBBfnFo%252BimpRt%252F8yrP0d%252Fz6ynSlL2kxaby%252F%252FcTOT%252Bh2uoH815d1%252BlEEpT9VZmyT6Vr9t1ax5mgPS1X3L8N80I05bFOvqRfRkYj3o%252F1Kqu9LobXw5tgPmESXTvsYz9tyBx%252Bf3vCjNY%252Fd%252FnW9vsReaqKgs6Nv7ZKZ4XC3%252FgJsakgJPwQAAA%253D%253D; hmClubLoggedFromIntegration=true; hmAgentId=null; _ga_PNVZ4XY35Y=GS1.1.1640734256.1.1.1640735053.0; _hjSessionUser_527543=eyJpZCI6IjdkMTE0YjFlLWJkYWYtNTRkNy05NTBkLTU1NmRhMTc0ZTI2MSIsImNyZWF0ZWQiOjE2NDA3MzQyNTYzMzcsImV4aXN0aW5nIjp0cnVlfQ==; exp=FYO0xIM0SK24mOs_nl5rBQ.0; hmCookieConsent={%22consentGiven%22:true%2C%22consentDate%22:%222021-12-28T23:31:15.656Z%22%2C%22allowAdvertising%22:true%2C%22version%22:%220.0.3%22}; _hjSessionUser_1198065=eyJpZCI6ImNmZGZmNjBiLWYwMGEtNTMyOS04MGU4LTBiNjQzZjk2NjBlMyIsImNyZWF0ZWQiOjE2MzgzNDkzODMyMjYsImV4aXN0aW5nIjp0cnVlfQ==; _gcl_au=1.1.54974082.1640734256; gtm_channel={"source":"direct","medium":"none","campaign":"","gclid":"","channel":"Direct"}',
})

# m3u8_file = M3u8File(master_url).fetch(headers=headers)
# print(m3u8_file.data)

# download_file(remote_uris=("240/240.m3u8", "https://vod-akm.play.hotmart.com/video/bLOQDdA9R2/hls/240/240.m3u8?hdntl=exp=1640827826~acl=/*~data=hdntl~hmac=ce1f9cb70a38aa2e59e77f3f45996576c28db5877d1e18c7b9b182d1644400ca"),
#               local_direcotry_uri="~/Downloads", headers=headers)

if not os.path.exists(local_directory):
    print(f'Creatting "{local_directory}"')
    os.makedirs(local_directory, exist_ok=True)
    print(f'"{local_directory}" created')

# data = requests.get(master_url, headers=headers)
# print(data.status_code)

# with open(local_file_uri, 'wb')as file:
#     file.write(data.content)

# not working
# data = m3u8.load(uri=master_url, headers=headers)
# print(data.data)
