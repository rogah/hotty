from datetime import datetime

from .http_request import HttpRequest


class HttpRequests(object):
    def __init__(self, requests):
        self.requests = requests

    def latest(self):
        return list(
            map(
                lambda request: HttpRequest(request),
                sorted(self.requests, key=lambda request: request["timestamp"]),
            )
        )[-1]
