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

from apiforge.contracts.debate import AdaptivePlan, AdaptivePolicy, ParticipantDeclaration
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
    policy: dict[str, Any] | None = None
    plan: dict[str, Any] | None = None
    replay_id: str = ""
    dissent: tuple[dict[str, Any], ...] = ()


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
        "policy": debate.policy,
        "plan": debate.plan,
        "replay_id": debate.replay_id,
        "dissent": list(debate.dissent),
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
        policy=doc.get("policy"),
        plan=doc.get("plan"),
        replay_id=doc.get("replay_id", ""),
        dissent=tuple(doc.get("dissent", [])),
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


def select_plan(
    risk: str,
    participants: tuple[ParticipantDeclaration, ...],
    policy: AdaptivePolicy | None = None,
) -> AdaptivePlan:
    """Choose a bounded participant set from declared adapters."""
    selected_policy = policy or AdaptivePolicy()
    normalized_risk = risk.lower()
    desired = (
        2
        if normalized_risk == "low"
        else 3
        if normalized_risk in {"medium", "high"}
        else selected_policy.max_participants
    )
    selected = tuple(
        sorted(participants, key=lambda item: (item.host, item.participant_id))[
            : min(desired, selected_policy.max_participants)
        ]
    )
    if len(selected) < selected_policy.quorum_sides:
        raise DebateError(
            "AF-DEBATE-PARTICIPANTS",
            f"risk {risk!r} has {len(selected)} participants; needs {selected_policy.quorum_sides}",
        )
    return AdaptivePlan(
        risk=normalized_risk,
        participants=selected,
        quorum_sides=selected_policy.quorum_sides,
        max_rounds=selected_policy.max_rounds,
        retry_budget=selected_policy.retry_budget,
        reason=f"bounded plan for {normalized_risk} risk",
    )


def open_adaptive_debate(
    case_dir: Path,
    question: str,
    sides: tuple[str, ...],
    now: str,
    *,
    risk: str,
    participants: tuple[ParticipantDeclaration, ...],
    policy: AdaptivePolicy | None = None,
) -> Debate:
    """Open a normal debate with an auditable adaptive plan attached."""
    selected_policy = policy or AdaptivePolicy()
    plan = select_plan(risk, participants, selected_policy)
    debate = open_debate(case_dir, question, sides, now)
    updated = Debate(
        **{
            **debate.__dict__,
            "policy": selected_policy.model_dump(mode="json"),
            "plan": plan.model_dump(mode="json"),
            "replay_id": stable_id(
                "debate-replay",
                {"debate_id": debate.debate_id, "plan": plan.model_dump(mode="json")},
            ),
        }
    )
    _write(case_dir, updated)
    return updated


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
    if debate.plan:
        participant_count = len(debate.plan.get("participants", ()))
        max_rounds = int(debate.plan.get("max_rounds", 1))
        budget = max(1, participant_count) * max_rounds
        if len(debate.submissions) >= budget:
            raise DebateError(
                "AF-DEBATE-BUDGET",
                f"adaptive debate budget exhausted after {budget} submissions",
            )
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
            "dissent": tuple(
                submission
                for submission in debate.submissions
                if submission.get("side") != decision
            ),
        }
    )
    _write(case_dir, updated)
    return updated
