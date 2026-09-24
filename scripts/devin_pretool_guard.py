"""Fail-closed guard for Devin CLI/Desktop command hooks.

The hook receives a Devin lifecycle event as JSON on stdin.  It blocks a small
set of irreversible repository and deployment operations and otherwise stays
silent.  It is intentionally conservative: it does not grant permissions and
it does not replace the API Forge policy gate.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

BLOCKED_PATTERNS = (
    re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE),
    re.compile(r"\bgit\s+checkout\s+--\b", re.IGNORECASE),
    re.compile(r"\bgit\s+clean\s+-[a-z]*f", re.IGNORECASE),
    re.compile(r"\bgit\s+push\b[^\r\n]*\s--force(?:-with-lease)?\b", re.IGNORECASE),
    re.compile(r"\brm\s+-[a-z]*r[a-z]*f", re.IGNORECASE),
    re.compile(r"\bremove-item\b[^\r\n]*\b-recurse\b", re.IGNORECASE),
    re.compile(r"\bdocker\s+system\s+prune\b", re.IGNORECASE),
)


def _command(event: dict[str, Any]) -> str:
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command")
    return command if isinstance(command, str) else ""


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, TypeError):
        return 0
    if not isinstance(event, dict):
        return 0
    command = _command(event)
    matched = next((pattern.pattern for pattern in BLOCKED_PATTERNS if pattern.search(command)), None)
    if matched is None:
        return 0
    print(
        json.dumps(
            {
                "decision": "block",
                "reason": (
                    "API Forge blocks irreversible repository or Docker cleanup operations "
                    "from Devin hooks; use an explicit governed approval path."
                ),
                "pattern": matched,
                "code": "AF-DEVIN-DESTRUCTIVE-COMMAND",
            }
        )
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
