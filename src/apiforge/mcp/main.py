"""Entry point for ``apiforge-mcp`` — lazy SDK import with a named refusal.

``--surface full|compact`` (or ``APIFORGE_MCP_SURFACE``) picks the tool
surface; ``--host`` (or ``APIFORGE_HOST``) picks it from the declared host
projection. Full is the default.
"""

from __future__ import annotations

import argparse
import os
import sys

MCP_UNAVAILABLE = "AF-MCP-UNAVAILABLE"


def resolve_surface(argv: list[str] | None = None) -> str:
    parser = argparse.ArgumentParser(prog="apiforge-mcp")
    parser.add_argument("--surface", choices=("full", "compact"), default=None)
    parser.add_argument("--host", default=None)
    parser.add_argument("--protocol", choices=("legacy", "modern"), default=None)
    args = parser.parse_args(argv)
    if args.surface:
        return str(args.surface)
    host = args.host or os.environ.get("APIFORGE_HOST")
    if host:
        from apiforge.agentops.projection import project_host

        return project_host(host).mcp_surface
    return os.environ.get("APIFORGE_MCP_SURFACE", "full")


def resolve_protocol(argv: list[str] | None = None) -> str:
    parser = argparse.ArgumentParser(prog="apiforge-mcp")
    parser.add_argument("--surface", choices=("full", "compact"), default=None)
    parser.add_argument("--host", default=None)
    parser.add_argument("--protocol", choices=("legacy", "modern"), default=None)
    args = parser.parse_args(argv)
    return str(args.protocol or os.environ.get("APIFORGE_MCP_PROTOCOL", "legacy"))


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")
    surface = resolve_surface(argv)
    protocol = resolve_protocol(argv)
    try:
        from apiforge.mcp.server import build_server

        server = build_server(surface, protocol=protocol)
    except ImportError:
        print(
            f"{MCP_UNAVAILABLE}: the mcp package is not installed; "
            "unlock: pip install 'apiforge[mcp]'",
            file=sys.stderr,
        )
        return 2
    server.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
