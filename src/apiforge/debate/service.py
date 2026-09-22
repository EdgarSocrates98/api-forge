"""Debate state machine: open -> submissions -> resolved|unresolved.

A debate is a file inside the case directory — canonical JSON, rewritten
atomically. Positions carry `fact_id` evidence (a position without evidence
is an opinion, and opinions are refused). Closing requires a referee name
and submissions on at least two distinct sides; a debate that cannot be
decided is closed `unresolved` with the referee's reason — the disagreement
stays on record either way.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apiforge.core.ids import stable_id

_QUORUM_SIDES = 2


class DebateError(ValueError):
    """A refused debate transition; ``str()`` begins with the AF code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class Debate:
    debate_id: str
    question: str
    sides: tuple[str, ...]
    opened_at: str
    submissions: tuple[dict[str, Any], ...] = ()
    status: str = "open"  # open | resolved | unresolved
    decision: str = ""
    referee: str = ""
    closed_at: str = ""


def _path(case_dir: Path, debate_id: str) -> Path:
    return case_dir / "debates" / f"{debate_id}.json"


def _write(case_dir: Path, debate: Debate) -> Path:
    out = _path(case_dir, debate.debate_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "debate_id": debate.debate_id,
        "question": debate.question,
        "sides": list(debate.sides),
        "opened_at": debate.opened_at,
        "submissions": list(debate.submissions),
        "status": debate.status,
        "decision": debate.decision,
        "referee": debate.referee,
        "closed_at": debate.closed_at,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def _load(case_dir: Path, debate_id: str) -> Debate:
    path = _path(case_dir, debate_id)
    if not path.is_file():
        raise DebateError("AF-DEBATE-NOT-FOUND", f"no debate {debate_id} in {case_dir}")
    doc = json.loads(path.read_text(encoding="utf-8"))
    return Debate(
        debate_id=doc["debate_id"],
        question=doc["question"],
        sides=tuple(doc["sides"]),
        opened_at=doc["opened_at"],
        submissions=tuple(doc.get("submissions", [])),
        status=doc.get("status", "open"),
        decision=doc.get("decision", ""),
        referee=doc.get("referee", ""),
        closed_at=doc.get("closed_at", ""),
    )


def _require_open(debate: Debate) -> None:
    if debate.status != "open":
        raise DebateError("AF-DEBATE-CLOSED", f"{debate.debate_id} is {debate.status}")


def open_debate(case_dir: Path, question: str, sides: tuple[str, ...], now: str) -> Debate:
    """Open a debate; `now` is the only clock."""
    if len(set(sides)) < _QUORUM_SIDES:
        raise DebateError("AF-DEBATE-SIDES", f"debate needs >= {_QUORUM_SIDES} distinct sides")
    debate_id = stable_id("debate", {"question": question, "sides": sorted(sides), "opened": now})
    debate = Debate(
        debate_id=debate_id,
        question=question,
        sides=tuple(sorted(set(sides))),
        opened_at=now,
    )
    _write(case_dir, debate)
    return debate


def submit(
    case_dir: Path,
    debate_id: str,
    side: str,
    position: str,
    evidence: tuple[str, ...],
) -> Debate:
    """Append a position; every position must cite fact_id evidence."""
    debate = _load(case_dir, debate_id)
    _require_open(debate)
    if side not in debate.sides:
        raise DebateError("AF-DEBATE-SIDE", f"{side!r} not among sides {sorted(debate.sides)}")
    if not evidence or not all(e.startswith("fact:") for e in evidence):
        raise DebateError("AF-DEBATE-NO-EVIDENCE", "positions must cite fact_id evidence")
    submission = {
        "side": side,
        "position": position,
        "evidence": sorted(set(evidence)),
        "order": len(debate.submissions) + 1,
    }
    updated = Debate(**{**debate.__dict__, "submissions": (*debate.submissions, submission)})
    _write(case_dir, updated)
    return updated


def close(
    case_dir: Path,
    debate_id: str,
    referee: str,
    decision: str | None,
    now: str,
) -> Debate:
    """Close as resolved (decision) or unresolved (decision=None)."""
    debate = _load(case_dir, debate_id)
    _require_open(debate)
    covered = {s["side"] for s in debate.submissions}
    if len(covered) < _QUORUM_SIDES:
        raise DebateError(
            "AF-DEBATE-NO-QUORUM",
            f"submissions cover {sorted(covered)}; need >= {_QUORUM_SIDES} sides",
        )
    status = "resolved" if decision else "unresolved"
    updated = Debate(
        **{
            **debate.__dict__,
            "status": status,
            "decision": decision or "recorded unresolved — disagreement stands",
            "referee": referee,
            "closed_at": now,
        }
    )
    _write(case_dir, updated)
    return updated
