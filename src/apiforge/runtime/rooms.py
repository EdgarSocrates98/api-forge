"""Decision rooms backed by the existing evidence-bound debate service."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.agentic import DecisionRecord
from apiforge.core.ids import stable_id
from apiforge.debate.service import close, open_debate, submit


def open_room(
    case_dir: Path,
    run_id: str,
    question: str,
    sides: tuple[str, ...],
    now: str,
) -> DecisionRecord:
    debate = open_debate(case_dir, question, sides, now)
    return DecisionRecord(
        decision_id=stable_id("decision", {"run_id": run_id, "debate_id": debate.debate_id}),
        run_id=run_id,
        question=question,
        options=debate.sides,
        status="awaiting_supervision",
        reason=debate.debate_id,
    )


def submit_position(
    case_dir: Path,
    debate_id: str,
    side: str,
    position: str,
    evidence: tuple[str, ...],
) -> dict[str, object]:
    debate = submit(case_dir, debate_id, side, position, evidence)
    return {"debate_id": debate.debate_id, "submissions": len(debate.submissions)}


def close_room(
    case_dir: Path,
    debate_id: str,
    referee: str,
    decision: str | None,
    now: str,
) -> dict[str, object]:
    debate = close(case_dir, debate_id, referee, decision, now)
    return {
        "debate_id": debate.debate_id,
        "status": debate.status,
        "decision": debate.decision,
        "referee": debate.referee,
    }
