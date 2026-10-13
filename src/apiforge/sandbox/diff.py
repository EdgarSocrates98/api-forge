"""Unified diff parsing. Refuses binary and mode-only patches by name."""

from __future__ import annotations

import re
from dataclasses import dataclass


class SandboxError(RuntimeError):
    def __init__(self, code: str, detail: str, field: str | None = None) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.field = field


@dataclass(frozen=True)
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: tuple[str, ...]


@dataclass(frozen=True)
class Patch:
    old_path: str | None
    new_path: str | None
    hunks: tuple[Hunk, ...]


_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def _side_path(token: str) -> str | None:
    if token == "/dev/null":
        return None
    for prefix in ("a/", "b/"):
        if token.startswith(prefix):
            return token[len(prefix) :]
    return token


def parse_unified_diff(text: str) -> tuple[Patch, ...]:
    patches: list[Patch] = []
    old_path: str | None = None
    new_path: str | None = None
    hunks: list[Hunk] = []
    saw_headers = False
    saw_mode_only = False
    lines = text.splitlines()
    i = 0

    def flush() -> None:
        nonlocal old_path, new_path, hunks, saw_headers, saw_mode_only
        if saw_mode_only and not hunks and not saw_headers:
            raise SandboxError(
                "AF-SANDBOX-MODE-ONLY",
                "mode-only changes carry no content and are refused",
            )
        if saw_headers or hunks:
            patches.append(Patch(old_path, new_path, tuple(hunks)))
        old_path = new_path = None
        hunks = []
        saw_headers = False
        saw_mode_only = False

    while i < len(lines):
        line = lines[i]
        if line.startswith(("Binary files", "GIT binary patch")):
            raise SandboxError(
                "AF-SANDBOX-BINARY-PATCH",
                "binary patches cannot be applied to a copied text tree",
            )
        if line.startswith("diff --git"):
            flush()
        elif line.startswith(("old mode", "new mode")):
            saw_mode_only = True
        elif line.startswith("--- "):
            old_path = _side_path(line[4:].strip())
            saw_headers = True
        elif line.startswith("+++ "):
            new_path = _side_path(line[4:].strip())
        elif line.startswith("@@ "):
            m = _HUNK_RE.match(line)
            if not m:
                raise SandboxError("AF-SANDBOX-BINARY-PATCH", f"malformed hunk: {line}")
            old_start = int(m.group(1))
            old_count = int(m.group(2) or 1)
            new_start = int(m.group(3))
            new_count = int(m.group(4) or 1)
            i += 1
            body: list[str] = []
            need_old, need_new = old_count, new_count
            while i < len(lines) and (need_old > 0 or need_new > 0):
                hl = lines[i]
                if hl.startswith("\\"):
                    body.append(hl)
                elif hl.startswith("+"):
                    body.append(hl)
                    need_new -= 1
                elif hl.startswith("-"):
                    body.append(hl)
                    need_old -= 1
                else:
                    body.append(" " + hl if hl else " ")
                    need_old -= 1
                    need_new -= 1
                i += 1
            if need_old > 0 or need_new > 0:
                raise SandboxError("AF-SANDBOX-BINARY-PATCH", "truncated hunk body")
            hunks.append(Hunk(old_start, old_count, new_start, new_count, tuple(body)))
            continue
        i += 1
    flush()
    return tuple(patches)


def apply_hunks(original: list[str], hunks: tuple[Hunk, ...]) -> list[str]:
    """Apply hunks to original lines (without newline terminators)."""
    result: list[str] = []
    cursor = 0
    for hunk in hunks:
        # With old_count == 0 the hunk inserts after `old_start`; otherwise the
        # hunk starts covering `old_start` itself (1-based).
        target = hunk.old_start if hunk.old_count == 0 else hunk.old_start - 1
        result.extend(original[cursor:target])
        cursor = target
        for line in hunk.lines:
            if line.startswith("\\"):
                continue
            marker, content = line[0], line[1:]
            if marker == "-":
                cursor += 1
            elif marker == "+":
                result.append(content)
            else:
                result.append(content)
                cursor += 1
    result.extend(original[cursor:])
    return result
