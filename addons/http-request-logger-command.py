"""
Capture HTTP request command.

Example:
mitmproxy --view-filter "master.*\.m3u8" -p 8081 -s [path/to/]http-request-headers-logger.py

:
"""

from datetime import datetime
import json
import os
import typing

from mitmproxy import flowfilter, ctx, flow, http, command, types


DEFAULT_OUTPUT = "~/.hotty/headers.json"


class HttpRequestLoggerCommand:
    @command.command("hotty.dump")
    def dump(
        self, flows: typing.Sequence[flow.Flow], output: types.Path = DEFAULT_OUTPUT
    ) -> None:
        for flow in flows:
            if isinstance(flow, http.HTTPFlow):
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

                data = {
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

                try:
                    path = os.path.dirname(output)
                    if not os.path.exists(path):
                        os.makedirs(path, exist_ok=True)
                except:
                    ctx.log.error(f"Hotty: Error creating output path {path}")

                try:
                    if os.path.exists(output):
                        os.remove(output)
                except:
                    ctx.log.error(f"Hotty: Error while deleting file {output}")

                try:
                    with open(output, "w") as outfile:
                        json.dump(data, outfile, indent=4, sort_keys=True)
                except:
                    ctx.log.error(f"Hotty: Error while dumping the file {output}")

                if os.path.exists(output):
                    ctx.log.info(
                        f"Hotty: Headers captured for '{flow.request.method} {flow.request.path}' in file {output}"
                    )
        ctx.log.alert("Hotty: done.")


addons = [HttpRequestLoggerCommand()]
