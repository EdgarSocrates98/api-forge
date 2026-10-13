"""Observe the installed optional MCP SDK; never contacts a server."""

from __future__ import annotations

import importlib.metadata
import json


def main() -> int:
    report: dict[str, object] = {
        "schema": "apiforge/mcp-protocol-observation/v1",
        "target_protocol": "2026-07-28",
        "status": "unresolved",
    }
    try:
        report["sdk_version"] = importlib.metadata.version("mcp")
        from mcp import types

        report["latest_protocol_version"] = getattr(types, "LATEST_PROTOCOL_VERSION", None)
        report["supported_protocol_versions"] = getattr(types, "SUPPORTED_PROTOCOL_VERSIONS", None)
        report["status"] = "observed"
    except (ImportError, importlib.metadata.PackageNotFoundError) as exc:
        report["reason"] = f"optional MCP SDK unavailable: {exc}"
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
