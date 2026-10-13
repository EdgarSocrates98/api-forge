"""Local read-only IDE/UI host for a canonical change-control run."""

from __future__ import annotations

import json
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

from apiforge.application.change_publishers import (
    render_html,
    render_junit,
    render_markdown,
    render_sarif,
)
from apiforge.contracts.base import ContractError
from apiforge.contracts.change_control import ChangeControlResult

Surface = Literal["ide", "ui"]


class ChangeHostError(ContractError):
    """A refused remote host configuration with an actionable unlock."""

    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        self.field = field
        self.unlock = unlock
        super().__init__(code, detail)


def load_change_result(run_dir: Path) -> ChangeControlResult:
    """Load the canonical result used by every host surface."""
    result_path = run_dir / "result.json"
    if not result_path.is_file():
        raise FileNotFoundError(result_path)
    return ChangeControlResult.model_validate(json.loads(result_path.read_text(encoding="utf-8")))


def surface_projection(run_dir: Path, surface: Surface) -> dict[str, Any]:
    """Return a host envelope without changing canonical status or evidence."""
    result = load_change_result(run_dir)
    return {
        "surface": surface,
        "contract": "CapabilityResult/v1",
        "result": result.model_dump(mode="json"),
    }


def render_ui_document(run_dir: Path) -> str:
    """Render a dependency-free visual document for a local browser host."""
    projection = surface_projection(run_dir, "ui")
    result = projection["result"]
    payload = json.dumps(projection, ensure_ascii=True, sort_keys=True)
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>API Forge change-control</title>
<style>body{{font:16px system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem}}
code,pre{{background:#f4f4f4;padding:.2rem .4rem;border-radius:4px}}
.status{{font-weight:700;color:#135d2c}} .gap{{color:#8a3b00}}</style></head>
<body><h1>API Forge change-control</h1>
<p>Canonical status: <span class="status">{result["status"]}</span>;
state: <code>{result["state"]}</code></p>
<h2>Gaps</h2><ul id="gaps"></ul>
<h2>Evidence</h2><ul id="evidence"></ul>
<details><summary>CapabilityResult/v1</summary><pre id="json"></pre></details>
<script>
const projection = {payload};
const result = projection.result;
for (const [id, values] of [["gaps", result.gaps], ["evidence", result.evidence]]) {{
  const list = document.getElementById(id);
  for (const value of values) {{ const item = document.createElement("li");
    item.textContent = value; item.className = id === "gaps" ? "gap" : ""; list.append(item); }}
}}
document.getElementById("json").textContent = JSON.stringify(projection, null, 2);
</script></body></html>"""


def _handler(run_dir: Path, auth_token: str | None) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _send(self, content: bytes, content_type: str, status: int = 200) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            try:
                if path == "/healthz":
                    self._send(b'{"status":"ok"}\n', "application/json")
                    return
                if path == "/readyz":
                    load_change_result(run_dir)
                    self._send(b'{"status":"ready"}\n', "application/json")
                    return
                result = load_change_result(run_dir)
                if auth_token is not None and self.headers.get("Authorization") != (
                    f"Bearer {auth_token}"
                ):
                    self._send(b"unauthorized\n", "text/plain; charset=utf-8", 401)
                    return
                if path == "/":
                    self._send(
                        render_ui_document(run_dir).encode("utf-8"), "text/html; charset=utf-8"
                    )
                elif path == "/api/result":
                    self._send(
                        (json.dumps(result.model_dump(mode="json"), sort_keys=True) + "\n").encode(
                            "utf-8"
                        ),
                        "application/json",
                    )
                elif path == "/api/ide":
                    self._send(
                        (
                            json.dumps(surface_projection(run_dir, "ide"), sort_keys=True) + "\n"
                        ).encode("utf-8"),
                        "application/json",
                    )
                elif path == "/api/ui":
                    self._send(
                        (
                            json.dumps(surface_projection(run_dir, "ui"), sort_keys=True) + "\n"
                        ).encode("utf-8"),
                        "application/json",
                    )
                elif path == "/reports/change-control.junit.xml":
                    metrics_path = run_dir / "metrics.json"
                    metrics = (
                        json.loads(metrics_path.read_text(encoding="utf-8"))
                        if metrics_path.is_file()
                        else {}
                    )
                    self._send(render_junit(result, metrics).encode("utf-8"), "application/xml")
                elif path == "/reports/change-control.md":
                    self._send(
                        render_markdown(result).encode("utf-8"), "text/markdown; charset=utf-8"
                    )
                elif path == "/reports/change-control.sarif.json":
                    self._send(render_sarif(result).encode("utf-8"), "application/json")
                elif path == "/reports/change-control.html":
                    self._send(render_html(result).encode("utf-8"), "text/html; charset=utf-8")
                else:
                    self._send(b"not found\n", "text/plain; charset=utf-8", 404)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                self._send(str(exc).encode("utf-8"), "text/plain; charset=utf-8", 500)

        def log_message(self, format: str, *args: object) -> None:
            return

    return Handler


def serve_change_control(
    run_dir: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    auth_token: str | None = None,
    tls_cert: Path | None = None,
    tls_key: Path | None = None,
    trust_proxy: bool = False,
) -> None:
    """Serve the read-only IDE/UI bridge locally or as an authenticated TLS host."""
    remote = host not in {"127.0.0.1", "localhost", "::1"}
    if remote and not auth_token:
        raise ChangeHostError(
            "AF-CHANGE-HOST-AUTH",
            "remote host requires a bearer token",
            field="auth_token",
            unlock="set APIFORGE_HOST_TOKEN and pass --token-env APIFORGE_HOST_TOKEN",
        )
    if (tls_cert is None) != (tls_key is None):
        raise ChangeHostError(
            "AF-CHANGE-HOST-TLS",
            "TLS certificate and key must be configured together",
            field="tls_cert/tls_key",
            unlock="provide both --tls-cert and --tls-key, or terminate TLS in a trusted proxy",
        )
    if remote and tls_cert is None and not trust_proxy:
        raise ChangeHostError(
            "AF-CHANGE-HOST-TLS",
            "remote host requires TLS or an explicitly trusted TLS-terminating proxy",
            field="tls_cert/tls_key/trust_proxy",
            unlock="provide both TLS files or pass --trust-proxy only behind a trusted HTTPS proxy",
        )
    server = ThreadingHTTPServer((host, port), _handler(Path(run_dir), auth_token))
    if tls_cert is not None and tls_key is not None:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=tls_cert, keyfile=tls_key)
        server.socket = context.wrap_socket(server.socket, server_side=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
