"""dispatch run: deterministic steps execute, the rest name why they wait."""

from __future__ import annotations

from pathlib import Path

import pytest

from apiforge.dispatch.mirrors import mirror_drift, sync_mirrors
from apiforge.dispatch.runner import DispatchContext, DispatchError, run_playbook

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
CONTRACT = FIXTURES / "openapi" / "orders-v1.yaml"
PROJECT = FIXTURES / "fastapi_orders"


def _ctx(case: Path, **kw: object) -> DispatchContext:
    return DispatchContext(case=case, **kw)  # type: ignore[arg-type]


def test_governance_playbook_runs_deterministic_steps(tmp_path: Path) -> None:
    ctx = _ctx(
        tmp_path, contract=CONTRACT, project=PROJECT, now="2026-09-21T12:00:00Z"
    )
    record = run_playbook("api-governance-reviewer", ctx)
    statuses = {s["verb"].split(" --")[0]: s["status"] for s in record["steps"]}
    assert statuses["discover"] == "ran"
    assert statuses["analyze"] == "ran"
    assert statuses["judge"] == "ran"
    assert statuses["evidence emit"] == "ran"  # analyze persisted the case
    # next-step needs a findings file that was not provided
    nxt = next(s for s in record["steps"] if s["verb"] == "next-step")
    assert nxt["status"] == "error" or nxt["status"] == "pending"
    assert (tmp_path / "dispatch").is_dir()
    ran = [s for s in record["steps"] if s["status"] == "ran"]
    assert all(s["output_sha256"] for s in ran)


def test_missing_inputs_become_pending_not_errors(tmp_path: Path) -> None:
    record = run_playbook("api-contract-architect", _ctx(tmp_path))
    assert record["ran"] == 1  # only "rules list" needs no inputs
    build = next(s for s in record["steps"] if s["verb"] == "model build")
    assert build["status"] == "pending"
    assert set(build["missing"]) == {"contract", "project"}
    # rules verbs need no inputs — they run even on an empty context
    rules = next(s for s in record["steps"] if s["verb"].startswith("rules list"))
    assert rules["status"] == "ran"


def test_collect_is_never_dispatched(tmp_path: Path) -> None:
    record = run_playbook("aws-api-infra-reviewer", _ctx(tmp_path))
    collect = next(s for s in record["steps"] if s["verb"].startswith("collect"))
    assert collect["status"] == "refused"
    assert "AWS" in collect["reason"]


def test_unknown_coordinator_named(tmp_path: Path) -> None:
    with pytest.raises(DispatchError, match="AF-DISPATCH-NO-PLAYBOOK"):
        run_playbook("not-a-coordinator", _ctx(tmp_path))


def test_mirrors_sync_and_drift(tmp_path: Path) -> None:
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "coord-a.md").write_text("---\nname: coord-a\n---\nbody\n")
    (agents / "executors").mkdir()
    (agents / "executors" / "ex.md").write_text("not mirrored\n")

    result = sync_mirrors(tmp_path)
    assert result["coordinators"] == 1
    for mirror in (".agents/agents", ".claude/agents"):
        assert (tmp_path / mirror / "coord-a.md").read_text().endswith("body\n")
        assert not (tmp_path / mirror / "ex.md").exists()
    assert mirror_drift(tmp_path) == []

    (tmp_path / ".claude" / "agents" / "coord-a.md").write_text("drifted\n")
    assert mirror_drift(tmp_path) == [".claude/agents/coord-a.md"]
