"""Closed command filters for RTK-style output normalization."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandFilter:
    name: str
    strip_patterns: tuple[str, ...]
    description: str


FILTERS: dict[str, CommandFilter] = {
    "pytest": CommandFilter("pytest", (r"^={3,}.*={3,}$", r"^collecting "), "test progress"),
    "mvn": CommandFilter("mvn", (r"^\[INFO\] ---.*---$", r"^Downloading from "), "Maven noise"),
    "gradle": CommandFilter("gradle", (r"^> Task :", r"^Downloading "), "Gradle progress"),
    "go test": CommandFilter("go test", (r"^\?$.*\[no test files\]$",), "Go package noise"),
    "terraform": CommandFilter(
        "terraform", (r"^Terraform used the selected providers",), "Terraform preamble"
    ),
    "k6": CommandFilter("k6", (r"^\s*\|\s*\\",), "k6 progress"),
}


def get_filter(command: str) -> CommandFilter | None:
    """Resolve the longest declared command prefix."""
    normalized = command.strip().lower()
    matches = [
        item
        for key, item in FILTERS.items()
        if normalized == key or normalized.startswith(key + " ")
    ]
    return max(matches, key=lambda item: len(item.name), default=None)


def apply_filter(text: str, command: str) -> str:
    """Remove only declared command noise; unknown commands remain unchanged."""
    selected = get_filter(command)
    if selected is None:
        return text
    patterns = tuple(re.compile(pattern, re.IGNORECASE) for pattern in selected.strip_patterns)
    return "\n".join(
        line for line in text.splitlines() if not any(pattern.search(line) for pattern in patterns)
    )


def list_filters() -> list[dict[str, object]]:
    return [
        {
            "name": item.name,
            "description": item.description,
            "strip_patterns": list(item.strip_patterns),
        }
        for item in sorted(FILTERS.values(), key=lambda value: value.name)
    ]
