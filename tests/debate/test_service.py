"""debate service: open -> submit -> resolved|unresolved, quorum enforced."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.debate.service import DebateError, close, open_debate, submit

NOW = "2026-09-21T12:00:00Z"


def _open(case: Path) -> str:
    d = open_debate(case, "sync vs async?", ("sync", "async"), NOW)
    return d.debate_id


def test_open_persists_debate(tmp_path: Path) -> None:
    did = _open(tmp_path)
    doc = json.loads(
        (tmp_path / "debates" / f"{did}.json").read_text(encoding="utf-8")
    )
    assert doc["status"] == "open"
    assert doc["question"] == "sync vs async?"


def test_single_side_refused(tmp_path: Path) -> None:
    with pytest.raises(DebateError, match="AF-DEBATE-SIDES"):
        open_debate(tmp_path, "q", ("only", "only"), NOW)


def test_submit_requires_fact_evidence(tmp_path: Path) -> None:
    did = _open(tmp_path)
    with pytest.raises(DebateError, match="AF-DEBATE-NO-EVIDENCE"):
        submit(tmp_path, did, "sync", "threads are simpler", ())
    with pytest.raises(DebateError, match="AF-DEBATE-NO-EVIDENCE"):
        submit(tmp_path, did, "sync", "opinion", ("finding:xyz",))


def test_submit_unknown_side_refused(tmp_path: Path) -> None:
    did = _open(tmp_path)
    with pytest.raises(DebateError, match="AF-DEBATE-SIDE"):
        submit(tmp_path, did, "middle", "q", ("fact:a",))


def test_close_requires_quorum(tmp_path: Path) -> None:
    did = _open(tmp_path)
    submit(tmp_path, did, "sync", "threads", ("fact:a",))
    with pytest.raises(DebateError, match="AF-DEBATE-NO-QUORUM"):
        close(tmp_path, did, "ref", "go sync", NOW)


def test_resolved_and_unresolved_close(tmp_path: Path) -> None:
    did = _open(tmp_path)
    submit(tmp_path, did, "sync", "threads", ("fact:a",))
    submit(tmp_path, did, "async", "coroutines", ("fact:b",))
    d = close(tmp_path, did, "ref", "go async — IO-bound", NOW)
    assert d.status == "resolved"
    assert d.referee == "ref"

    did2 = _open(tmp_path)
    submit(tmp_path, did2, "sync", "s", ("fact:c",))
    submit(tmp_path, did2, "async", "a", ("fact:d",))
    d2 = close(tmp_path, did2, "ref", None, NOW)
    assert d2.status == "unresolved"
    assert "unresolved" in d2.decision


def test_closed_debate_refuses_mutation(tmp_path: Path) -> None:
    did = _open(tmp_path)
    submit(tmp_path, did, "sync", "s", ("fact:a",))
    submit(tmp_path, did, "async", "a", ("fact:b",))
    close(tmp_path, did, "ref", "done", NOW)
    with pytest.raises(DebateError, match="AF-DEBATE-CLOSED"):
        submit(tmp_path, did, "sync", "late", ("fact:e",))


def test_missing_debate_named(tmp_path: Path) -> None:
    with pytest.raises(DebateError, match="AF-DEBATE-NOT-FOUND"):
        submit(tmp_path, "debate:nope", "sync", "s", ("fact:a",))


def test_debate_id_is_deterministic(tmp_path: Path) -> None:
    a = open_debate(tmp_path / "a", "q?", ("x", "y"), NOW)
    b = open_debate(tmp_path / "b", "q?", ("x", "y"), NOW)
    assert a.debate_id == b.debate_id
