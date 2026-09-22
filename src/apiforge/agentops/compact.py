"""Deterministic RTK-style command output compaction.

The adapter reduces transport noise while keeping critical evidence in the
emitted payload. It never executes commands and never replaces the complete
artifact, which remains the source of truth for verification and replay.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from apiforge.agentops.filters import apply_filter


class CavemanMode(StrEnum):
    """Output posture shared by host integrations."""

    OFF = "off"
    LITE = "lite"
    FULL = "full"
    ULTRA = "ultra"
    WENYAN = "wenyan"


_MODE_LIMITS: dict[CavemanMode, int | None] = {
    CavemanMode.OFF: None,
    CavemanMode.LITE: 120,
    CavemanMode.FULL: 80,
    CavemanMode.ULTRA: 40,
    CavemanMode.WENYAN: 20,
}

_ANSI = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")
_PROGRESS = re.compile(
    r"^(?:\s*(?:\d{1,3}%|[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏])\s*$|\s*(?:downloading|installing|building)\.\.\.$)",
    re.IGNORECASE,
)
_CRITICAL = re.compile(
    r"(?:AF-[A-Z0-9-]+|error|exception|traceback|fatal|failed|failure|panic|blocked|refused|denied|warning|\b(?:4|5)\d\d\b|assert(?:ion)?error|segmentation fault|exit code)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CompactedOutput:
    """Compact result with enough provenance to audit the transformation."""

    command: str
    text: str
    mode: str
    original_bytes: int
    emitted_bytes: int
    original_lines: int
    emitted_lines: int
    omitted_lines: int
    critical_lines: int
    critical_evidence_preserved: bool
    source_sha256: str
    artifact: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "command": self.command,
            "text": self.text,
            "mode": self.mode,
            "original_bytes": self.original_bytes,
            "emitted_bytes": self.emitted_bytes,
            "original_lines": self.original_lines,
            "emitted_lines": self.emitted_lines,
            "omitted_lines": self.omitted_lines,
            "critical_lines": self.critical_lines,
            "critical_evidence_preserved": self.critical_evidence_preserved,
            "source_sha256": self.source_sha256,
            "artifact": self.artifact,
            "loss_policy": "no-critical-evidence-loss",
        }


def _clean_lines(text: str) -> tuple[list[str], list[int]]:
    cleaned: list[str] = []
    critical: list[int] = []
    for raw in text.splitlines():
        line = _ANSI.sub("", raw).rstrip()
        if not line.strip() or _PROGRESS.match(line):
            continue
        index = len(cleaned)
        cleaned.append(line)
        if _CRITICAL.search(line):
            critical.append(index)
    return cleaned, critical


def _select_indexes(total: int, critical: list[int], limit: int) -> list[int]:
    if total <= limit:
        return list(range(total))
    selected = set(critical)
    head = max(1, limit // 2)
    tail = max(1, limit - head)
    selected.update(range(min(head, total)))
    selected.update(range(max(0, total - tail), total))
    return sorted(selected)


def compact_text(
    text: str,
    *,
    command: str = "unknown",
    mode: CavemanMode | str = CavemanMode.FULL,
    max_lines: int | None = None,
    artifact: str | Path | None = None,
) -> CompactedOutput:
    """Compact deterministic text without dropping critical lines.

    ``text`` is the complete command output. The returned ``text`` is a
    transport projection; callers must retain the original artifact when
    ``omitted_lines`` is non-zero.
    """
    selected_mode = CavemanMode(mode)
    limit = _MODE_LIMITS[selected_mode] if max_lines is None else max_lines
    original_bytes = len(text.encode("utf-8"))
    source_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    filtered_text = apply_filter(text, command)
    lines, critical = _clean_lines(filtered_text)
    if limit is None:
        indexes = list(range(len(lines)))
    else:
        if limit < 1:
            raise ValueError("AF-COMPACT-LIMIT: max_lines must be positive")
        indexes = _select_indexes(len(lines), critical, limit)

    omitted = len(lines) - len(indexes)
    emitted: list[str] = []
    previous = -1
    for index in indexes:
        if index - previous > 1:
            emitted.append(f"[apiforge compacted {index - previous - 1} lines]")
        emitted.append(lines[index])
        previous = index
    if previous < len(lines) - 1:
        emitted.append(f"[apiforge compacted {len(lines) - previous - 1} lines]")
    result_text = "\n".join(emitted)
    if result_text:
        result_text += "\n"
    selected_critical = {index for index in indexes if index in set(critical)}
    return CompactedOutput(
        command=command,
        text=result_text,
        mode=selected_mode.value,
        original_bytes=original_bytes,
        emitted_bytes=len(result_text.encode("utf-8")),
        original_lines=len(lines),
        emitted_lines=len(emitted),
        omitted_lines=omitted,
        critical_lines=len(critical),
        critical_evidence_preserved=len(selected_critical) == len(critical),
        source_sha256=source_sha256,
        artifact=str(artifact) if artifact is not None else None,
    )


def compact_file(
    path: Path,
    *,
    command: str = "unknown",
    mode: CavemanMode | str = CavemanMode.FULL,
    max_lines: int | None = None,
) -> CompactedOutput:
    """Compact a UTF-8 artifact without modifying it."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"AF-COMPACT-INPUT-NOT-FOUND: {path}")
    return compact_text(
        path.read_text(encoding="utf-8", errors="replace"),
        command=command,
        mode=mode,
        max_lines=max_lines,
        artifact=path,
    )
