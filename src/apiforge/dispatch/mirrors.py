"""Agent mirrors: publish coordinators where host runtimes look for them.

Devin reads `.agents/agents/`, Claude Code reads `.claude/agents/` and Codex
reads `.codex/agents/`. Every mirror file is `render(source, host)` of an
`agents/*.md` coordinator (executors are not dispatchable profiles). The
release gate re-renders and compares — drift is a failure, not a warning.
Files in a mirror directory that are not generated agents are reported, never
deleted.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from apiforge.dispatch.agent_source import coordinator_paths
from apiforge.dispatch.render import CODEX_DIR, MIRROR_DIRS, render_all

_AGENT_MD = re.compile(r"\A---\r?\n(?:.*\r?\n)*?name:\s*\S", re.MULTILINE)
_AGENT_TOML = re.compile(r"^name\s*=", re.MULTILINE)


def generated_mirror_plan(root: Path) -> dict[str, object]:
    """Describe compatibility mirror output without changing consumer files."""

    rendered = render_all(Path(root))
    return {
        "source": "repository:agents",
        "mutation": "none",
        "artifacts": [
            {
                "source": str(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "targets": [
                    str(Path(root) / target)
                    for target in rendered
                    if Path(target).stem == path.stem
                ],
            }
            for path in coordinator_paths(Path(root))
        ],
        "limitations": ["legacy mirror publication remains an explicit local action"],
    }


def _suffix(mirror: str) -> str:
    return ".toml" if mirror == CODEX_DIR else ".md"


def _is_agent_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    pattern = _AGENT_TOML if path.suffix == ".toml" else _AGENT_MD
    return bool(pattern.search(text))


def _extras(root: Path, expected: dict[str, bytes]) -> list[tuple[str, Path, bool]]:
    extras: list[tuple[str, Path, bool]] = []
    for mirror in MIRROR_DIRS:
        target_dir = root / mirror
        if not target_dir.is_dir():
            continue
        for path in sorted(target_dir.glob(f"*{_suffix(mirror)}")):
            rel = f"{mirror}/{path.name}"
            if rel not in expected:
                extras.append((rel, path, _is_agent_file(path)))
    return extras


def sync_mirrors(root: Path) -> dict[str, object]:
    """Render every mirror from `agents/*.md`; returns what changed."""
    root = Path(root)
    expected = render_all(root)
    written: list[str] = []
    for rel, agent, is_agent in _extras(root, expected):
        if is_agent:
            agent.unlink()
            written.append(f"-{rel}")
    for rel, content in expected.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file() or target.read_bytes() != content:
            target.write_bytes(content)
            written.append(rel)
    return {"written": sorted(written), "coordinators": len(coordinator_paths(root))}


def mirror_drift(root: Path) -> list[str]:
    """Paths where a mirror diverges from its rendered source (or is missing/extra)."""
    root = Path(root)
    expected = render_all(root)
    drift: list[str] = []
    for rel, content in expected.items():
        target = root / rel
        if not target.is_file() or target.read_bytes() != content:
            drift.append(rel)
    for rel, _, is_agent in _extras(root, expected):
        drift.append(f"{rel} (orphan)" if is_agent else f"{rel} (non-agent file)")
    return sorted(drift)


__all__ = ["MIRROR_DIRS", "generated_mirror_plan", "mirror_drift", "sync_mirrors"]
