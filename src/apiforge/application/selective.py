"""Selective-agentics application facade shared by CLI and MCP."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any


def knowledge_select(
    intent: str,
    *,
    capability: str | None = None,
    frameworks: Sequence[str] = (),
    root: Path | None = None,
) -> dict[str, Any]:
    from apiforge.knowledge.selector import select_expertise

    selection = select_expertise(intent, capability=capability, frameworks=frameworks, root=root)
    return selection.model_dump(mode="json")


def debate_packet(
    case_dir: Path, debate_id: str, *, capsule_id: str | None = None, root: Path | None = None
) -> dict[str, Any]:
    from apiforge.debate.packet import referee_packet

    size = 0
    if capsule_id:
        size = _capsule_bytes(Path(root or Path.cwd()), capsule_id)
    return referee_packet(
        Path(case_dir), debate_id, capsule_id=capsule_id, capsule_bytes=size
    ).model_dump(mode="json")


def agents_audit(root: Path | None = None) -> dict[str, Any]:
    from apiforge.agentops.agent_audit import audit_agents

    return audit_agents(Path(root or Path.cwd()))


def _capsule_bytes(root: Path, capsule_id: str) -> int:
    """Expanded size of the capsule's refs recorded in the run ledger (0 when unknown)."""
    from apiforge.economy import run_ledger

    run = f"run-{capsule_id[-16:]}"
    total = 0
    for row in run_ledger.entries(root)[0]:
        if row.run_id == run and row.verb.startswith(("context capsule", "mcp:context_capsule")):
            total += sum(ref.size_bytes for ref in row.refs)
    return total


def parse_disagreements(values: Sequence[str]) -> tuple[tuple[str, str], ...]:
    from apiforge.debate.service import DebateError

    parsed: list[tuple[str, str]] = []
    for value in values:
        point, sep, reason = value.partition("=")
        if not sep or not point.strip():
            raise DebateError(
                "AF-DEBATE-DELTA-INVALID", f"--disagree {value!r} is not 'point=reason'"
            )
        parsed.append((point.strip(), reason.strip()))
    return tuple(parsed)


__all__ = ["agents_audit", "debate_packet", "knowledge_select", "parse_disagreements"]
