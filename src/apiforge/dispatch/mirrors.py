"""Agent mirrors: publish coordinators where host runtimes look for them.

Devin reads `.agents/agents/`, Claude Code reads `.claude/agents/` — both are
byte-identical copies of `agents/*.md` (coordinators only; executors are not
dispatchable profiles). The release gate regenerates and compares — drift is
a failure, not a warning.
"""

from __future__ import annotations

from pathlib import Path

MIRROR_DIRS = (".agents/agents", ".claude/agents")


def _coordinators(root: Path) -> list[Path]:
    agents_dir = root / "agents"
    return sorted(p for p in agents_dir.glob("*.md") if p.is_file())


def sync_mirrors(root: Path) -> dict[str, object]:
    """Regenerate both mirrors from `agents/*.md`; returns what changed."""
    written: list[str] = []
    for mirror in MIRROR_DIRS:
        target_dir = root / mirror
        target_dir.mkdir(parents=True, exist_ok=True)
        expected = {p.name for p in _coordinators(root)}
        for stale in target_dir.glob("*.md"):
            if stale.name not in expected:
                stale.unlink()
                written.append(f"-{mirror}/{stale.name}")
        for source in _coordinators(root):
            target = target_dir / source.name
            content = source.read_bytes()
            if not target.is_file() or target.read_bytes() != content:
                target.write_bytes(content)
                written.append(f"{mirror}/{source.name}")
    return {"written": sorted(written), "coordinators": len(_coordinators(root))}


def mirror_drift(root: Path) -> list[str]:
    """Paths where a mirror diverges from its `agents/` source (or is missing)."""
    drift: list[str] = []
    for mirror in MIRROR_DIRS:
        target_dir = root / mirror
        for source in _coordinators(root):
            target = target_dir / source.name
            if not target.is_file() or target.read_bytes() != source.read_bytes():
                drift.append(f"{mirror}/{source.name}")
        for extra in target_dir.glob("*.md"):
            if not (root / "agents" / extra.name).is_file():
                drift.append(f"{mirror}/{extra.name} (orphan)")
    return sorted(drift)
