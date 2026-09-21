"""Entry point for ``apiforge-mcp`` — lazy SDK import with a named refusal."""

from __future__ import annotations

import sys

MCP_UNAVAILABLE = "AF-MCP-UNAVAILABLE"


def main() -> int:
    try:
        from apiforge.mcp.server import build_server

        server = build_server()
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
