"""
Capture HTTP request headers.

Example:
mitmproxy --view-filter "master.*\.m3u8" -p 8081 -s [path/to/]http-request-headers-logger.py --set filter="master.*\.m3u8"
"""

from datetime import datetime
import json
import os

from mitmproxy import flowfilter, ctx


DEFAULT_OUTPUT = "~/.hotty/headers.json"


class HttpRequestHeadersLogger:
    def __init__(self):
        self.data = []
        self.filter = flowfilter.TFilter = None
        self.output = os.path.expanduser(DEFAULT_OUTPUT)

    def configure(self, updates):
        self.filter = flowfilter.parse(ctx.options.filter)
        self.output = (
            os.path.expanduser(ctx.options.output)
            if len(ctx.options.output)
            else os.path.expanduser(DEFAULT_OUTPUT)
        )

    def load(self, loader):
        loader.add_option(
            name="filter",
            typespec=str,
            default="",
            help="Check that flow matches filter.",
        )

        loader.add_option(
            name="output",
            typespec=str,
            default="",
            help=f"Path to save traced HTTP request header. Default {DEFAULT_OUTPUT}",
        )

    def request(self, flow):
        if flowfilter.match(self.filter, flow):

            query = {}
            if len(flow.request.query) > 0:
                for key, value in flow.request.query.items():
                    query[key] = value

            cookies = {}
            if len(flow.request.cookies) > 0:
                for key, value in flow.request.cookies.items():
                    cookies[key] = value

            headers = {}
            if len(flow.request.headers) > 0:
                for key, value in flow.request.headers.items():
                    headers[key] = value

            self.data.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "method": flow.request.method,
                    "scheme": flow.request.scheme,
                    "authority": flow.request.authority,
                    "host": flow.request.host,
                    "host_header": flow.request.host_header,
                    "port": flow.request.port,
                    "path": flow.request.path,
                    "url": flow.request.url,
                    "pretty_host": flow.request.pretty_host,
                    "pretty_url": flow.request.pretty_url,
                    "query": query,
                    "cookies": cookies,
                    "headers": headers,
                }
            )

            try:
                path = os.path.dirname(self.output)
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
            except:
                ctx.log.error(f"Hotty: Error creating output path {path}")

            try:
                if os.path.exists(self.output):
                    os.remove(self.output)
            except:
                ctx.log.error(f"Hotty: Error while deleting file {self.output}")

            try:
                with open(self.output, "w") as outfile:
                    json.dump(self.data, outfile, indent=4, sort_keys=True)
            except:
                ctx.log.error(f"Hotty: Error while dumping the file {self.output}")

            if os.path.exists(self.output):
                ctx.log.info(
                    f"Hotty: Headers captured for '{flow.request.method} {flow.request.url}' in file {self.output}"
                )


addons = [HttpRequestHeadersLogger()]
