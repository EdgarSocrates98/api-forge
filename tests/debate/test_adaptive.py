from pathlib import Path

import pytest

from apiforge.contracts.debate import AdaptivePolicy, ParticipantDeclaration
from apiforge.debate.service import DebateError, close, open_adaptive_debate, submit


def test_adaptive_debate_is_bounded_and_replayable(tmp_path: Path) -> None:
    participants = tuple(
        ParticipantDeclaration(participant_id=name, host=name, capabilities=("debate",))
        for name in ("codex", "claude", "devin", "copilot")
    )
    debate = open_adaptive_debate(
        tmp_path,
        "which plan?",
        ("safe", "fast"),
        "2026-09-23T00:00:00Z",
        risk="high",
        participants=participants,
        policy=AdaptivePolicy(max_participants=3, max_rounds=2),
    )
    assert debate.plan and len(debate.plan["participants"]) == 3
    submit(tmp_path, debate.debate_id, "safe", "evidence", ("fact:a",))
    submit(tmp_path, debate.debate_id, "fast", "evidence", ("fact:b",))
    closed = close(tmp_path, debate.debate_id, "referee", "safe", "2026-09-23T00:01:00Z")
    assert closed.replay_id
    assert closed.dissent


def test_adaptive_debate_refuses_submissions_over_budget(tmp_path: Path) -> None:
    participants = tuple(
        ParticipantDeclaration(participant_id=name, host=name) for name in ("codex", "claude")
    )
    debate = open_adaptive_debate(
        tmp_path,
        "bounded?",
        ("a", "b"),
        "2026-09-23T00:00:00Z",
        risk="low",
        participants=participants,
        policy=AdaptivePolicy(max_participants=2, max_rounds=1),
    )
    submit(tmp_path, debate.debate_id, "a", "one", ("fact:1",))
    submit(tmp_path, debate.debate_id, "b", "two", ("fact:2",))
    with pytest.raises(DebateError, match="AF-DEBATE-BUDGET"):
        submit(tmp_path, debate.debate_id, "a", "three", ("fact:3",))
