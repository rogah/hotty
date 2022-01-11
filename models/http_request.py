import json


class HttpRequest(object):
    def __init__(self, request):
        self.request = request

    def url(self):
        return self.request["url"]

    def method(self):
        return self.request["method"]

    def path(self):
        return self.request["path"]

    def headers(self):
        return self.request["headers"]

    def __repr__(self):
        return json.dumps(self.request)

    def __str__(self):
        return f"HttpRequest(url={self.request['url']})"


class HttpRequests(object):
    def __init__(self, requests):
        self.requests = requests

    def latest(self):
        sorted_requests = list(
            map(
                lambda request: HttpRequest(request),
                sorted(self.requests, key=lambda request: request["timestamp"]),
            )
        )
        return sorted_requests[-1]
