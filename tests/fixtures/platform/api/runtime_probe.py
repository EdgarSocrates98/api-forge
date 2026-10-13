from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/orders":
            body = b'[{"order_id":"runtime"}]'
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *_: object) -> None:
        return


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
Thread(target=server.serve_forever, daemon=True).start()
try:
    with urlopen(f"http://127.0.0.1:{server.server_port}/orders", timeout=2) as response:
        assert response.status == 200
        assert json.loads(response.read()) == [{"order_id": "runtime"}]
finally:
    server.shutdown()

print(json.dumps({"status": "passed", "checks": ["HTTP GET /orders", "JSON response"]}))
