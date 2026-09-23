"""Local read-only IDE/UI host for a canonical change-control run."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

from apiforge.application.change_publishers import render_junit, render_markdown
from apiforge.contracts.change_control import ChangeControlResult

Surface = Literal["ide", "ui"]


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


def _handler(run_dir: Path) -> type[BaseHTTPRequestHandler]:
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
                result = load_change_result(run_dir)
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
                else:
                    self._send(b"not found\n", "text/plain; charset=utf-8", 404)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                self._send(str(exc).encode("utf-8"), "text/plain; charset=utf-8", 500)

        def log_message(self, format: str, *args: object) -> None:
            return

    return Handler


def serve_change_control(run_dir: Path, *, host: str = "127.0.0.1", port: int = 8765) -> None:
    """Serve the read-only UI/IDE bridge until interrupted by the host."""
    server = ThreadingHTTPServer((host, port), _handler(Path(run_dir)))
    try:
        server.serve_forever()
    finally:
        server.server_close()
