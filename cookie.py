"""
Capture HTTP request headers.

Example:
mitmproxy --view-filter "master.*\.m3u8" -p 8081 -s cookie.py --set filter="master.*\.m3u8"
"""
from mitmproxy import flowfilter, ctx, exceptions
import json
import os


DEFAULT_OUTPUT = "~/.hotty/.headers.json"


class RequestLogger:
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

            cookies = []
            if len(flow.request.cookies) > 0:
                for key, value in flow.request.cookies.items():
                    cookies.append(f"{key}={value}")

            self.data.append(
                {
                    "method": flow.request.method,
                    "url": flow.request.url,
                    "cookie": ";".join(cookies),
                }
            )

            try:
                path = os.path.dirname(self.output)
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
            except:
                print("Error creating output path ", path)

            # cookies = type(flow.request.cookies)
            # ctx.log.info(f"#### Cookie Type: {cookies}")

            try:
                os.remove(self.output)
            except:
                print("Error while deleting file ", self.output)

            with open(self.output, "w") as outfile:
                json.dump(self.data, outfile)


addons = [RequestLogger()]
