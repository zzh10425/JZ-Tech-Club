#!/usr/bin/env python3
"""Serve a temporary preview without modifying the checked-in HTML files."""

from __future__ import annotations

import functools
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from generate_people import DIST, generate


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        if urlsplit(self.path).path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        super().do_GET()


def main() -> None:
    current_year = generate(DIST)
    handler = functools.partial(PreviewHandler, directory=str(DIST))
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        host, port = server.server_address[:2]
        url = f"http://{host}:{port}/"
        print("Preview server running:", flush=True)
        print(url, flush=True)
        print("Serving directory:", flush=True)
        print(DIST, flush=True)
        print(f"Generated dist for {current_year}.", flush=True)
        try:
            webbrowser.open(url)
        except Exception as error:  # Browser launching is optional.
            print(f"Could not open browser automatically: {error}", flush=True)
        print("Press Ctrl+C to stop the server.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping preview server.", flush=True)


if __name__ == "__main__":
    main()
