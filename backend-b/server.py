#!/usr/bin/env python3
"""Backend B — Aditya Verma (Mac 4), port 3002.
Supports Flask app (as run in live lab with Werkzeug) and stdlib fallback.
"""

import sys
import os

# Ensure local directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, HOST, PORT
    if __name__ == "__main__":
        print(f"Starting Flask Backend B on http://{HOST}:{PORT}")
        app.run(host=HOST, port=PORT)
except ImportError:
    import json
    from http.server import BaseHTTPRequestHandler, HTTPServer

    HOST = "0.0.0.0"
    PORT = 3002
    BACKEND_ID = "B"
    CACHE_ETAG = '"v1"'
    STATUS_ETAG = '"B-v1"'

    class BackendHandler(BaseHTTPRequestHandler):
        server_version = "Werkzeug/3.1.9 Python/3.13.5"

        def do_GET(self):
            etag = CACHE_ETAG if self.path == "/api/cached" else STATUS_ETAG
            if self.headers.get("If-None-Match") == etag:
                self.send_response(304)
                self.send_header("ETag", etag)
                self.send_header("Cache-Control", "max-age=60")
                self.send_header("X-Backend", BACKEND_ID)
                self.end_headers()
                return

            if self.path in ("/", ""):
                payload = {
                    "backend": BACKEND_ID,
                    "status": "ok",
                    "service": "TeamSnorlax",
                }
            elif self.path == "/api/status":
                payload = {"backend": BACKEND_ID, "status": "ok"}
            elif self.path == "/api/cached":
                payload = {"backend": BACKEND_ID, "data": "cacheable content"}
            else:
                body = json.dumps({"error": "not found"}).encode("utf-8")
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "max-age=60")
            self.send_header("ETag", etag)
            self.send_header("X-Backend", BACKEND_ID)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            print(f"[{BACKEND_ID}] {self.address_string()} - {fmt % args}")

    if __name__ == "__main__":
        server = HTTPServer((HOST, PORT), BackendHandler)
        print(f"Backend B running on http://{HOST}:{PORT}")
        print("Machine: Mac 4 | Member: Aditya Verma | Team Snorlax")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping Backend B...")
            server.server_close()
