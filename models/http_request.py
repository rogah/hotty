import json


class HttpRequest(object):
    def __init__(self, request):
        self.request = request

    def url(self):
        return self.request["url"]

    def __repr__(self):
        return json.dumps(self.request)

    def __str__(self):
        return f"HttpRequest(url={self.request['url']})"
