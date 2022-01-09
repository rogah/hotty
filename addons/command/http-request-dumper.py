"""
Capture HTTP request command.

Command name:   hotty.dump
Flow selector:  @all|@focus|@shown|@hidden|@marked|@unmarked    Refer https://docs.mitmproxy.org/stable/concepts-filters/#view-flow-selectors
Output path:    Optional. Default is ~/.hotty/requests.json

Example:
mitmproxy --view-filter "master.*\.m3u8" -p 8080 -s [path/to/]http-request-dumper.py

:hotty.dump @focus
:hotty.dump @shown ~/path/to/file.json
"""

from datetime import datetime
import json
import os
import typing

from mitmproxy import ctx, flow, http, command, types


DEFAULT_OUTPUT = "~/.hotty/requests.json"


def conver_to_object(dictionary):
    object = {}
    if len(dictionary) > 0:
        for key, value in dictionary.items():
            object[key] = value
    return object


def create_paths(output):
    try:
        path = os.path.dirname(output)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
    except:
        ctx.log.error(f"Hotty: Error creating output path {path}")


def remove_existing(output):
    try:
        if os.path.exists(output):
            os.remove(output)
    except:
        ctx.log.error(f"Hotty: Error while deleting file {output}")


def dump_request(data, output):
    try:
        with open(output, "w") as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)
    except:
        ctx.log.error(f"Hotty: Error while dumping the file {output}")


def validate_dump(output, http_method, url_path):
    if os.path.exists(output):
        ctx.log.info(
            f"Hotty: HTTP request captured for '{http_method} {url_path}' in file {output}"
        )


def validate_processed_data(data):
    processed_flows = len(data)
    if processed_flows > 0:
        ctx.log.alert(f"Hotty: total of {processed_flows} HTTP requests captured.")
    else:
        ctx.log.alert(f"Hotty: No HTTP requests captured.")


class HttpRequestDumper:
    @command.command("hotty.dump")
    def dump(
        self,
        flows: typing.Sequence[flow.Flow],
        output: types.Path = os.path.expanduser(DEFAULT_OUTPUT),
    ) -> None:

        data = []

        for flow in flows:
            if isinstance(flow, http.HTTPFlow):
                query = conver_to_object(flow.request.query)
                cookies = conver_to_object(flow.request.cookies)
                headers = conver_to_object(flow.request.headers)

                timestamp = datetime.now().isoformat()

                data.append(
                    {
                        "timestamp": timestamp,
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

                create_paths(output)

                remove_existing(output)

                dump_request(data=data, output=output)

                validate_dump(
                    output=output,
                    http_method=flow.request.method,
                    url_path=flow.request.path,
                )

        validate_processed_data(data)


addons = [HttpRequestDumper()]
