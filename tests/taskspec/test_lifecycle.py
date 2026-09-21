"""TaskSpec lifecycle: store, state machine, seal, run, acceptance, brief."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.application.analyze import analyze_project
from apiforge.brief.render import brief_for_task
from apiforge.contracts.base import ContractError
from apiforge.contracts.task import BriefStatus, TaskSpec, TaskState
from apiforge.taskspec import store
from apiforge.taskspec.runner import accept_task, run_task, task_status
from apiforge.taskspec.service import (
    create_task,
    ready_task,
    review_task,
    seal_task,
)


def _spec(task_id: str = "t-1", **kw: object) -> TaskSpec:
    return TaskSpec.model_validate(
        {"id": task_id, "outcome": "list the rules", **kw}
    )


def _keypair(tmp_path: Path) -> Path:
    from apiforge.report.keys import generate_keypair

    generate_keypair(tmp_path / "keys", "sealer")
    return tmp_path / "keys" / "sealer.pem"


def test_create_and_load(tmp_path: Path) -> None:
    spec = create_task(tmp_path, _spec())
    assert spec.state is TaskState.DRAFT
    assert store.load(tmp_path, "t-1").id == "t-1"
    assert store.history(tmp_path, "t-1")[0]["event"] == "created"


def test_duplicate_id_refused(tmp_path: Path) -> None:
    create_task(tmp_path, _spec())
    with pytest.raises(ContractError, match="AF-TASK-EXISTS"):
        create_task(tmp_path, _spec())


def test_bad_id_refused(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="AF-TASK-ID"):
        create_task(tmp_path, _spec("Bad Id!"))


def test_review_creates_revision_and_bumps(tmp_path: Path) -> None:
    create_task(tmp_path, _spec())
    spec = review_task(tmp_path, "t-1", "alice")
    assert spec.state is TaskState.REVIEWED and spec.revision == 1
    # a second review with a change bumps again
    spec = review_task(tmp_path, "t-1", "alice", {"outcome": "new outcome"})
    assert spec.revision == 2
    rev = store.task_dir(tmp_path, "t-1") / "revisions" / "2.json"
    assert rev.is_file()


def test_seal_requires_reviewed(tmp_path: Path) -> None:
    create_task(tmp_path, _spec())
    key = _keypair(tmp_path)
    with pytest.raises(ContractError, match="AF-TASK-TRANSITION"):
        seal_task(tmp_path, "t-1", key, "alice")


def test_seal_then_change_invalidates(tmp_path: Path) -> None:
    create_task(tmp_path, _spec())
    review_task(tmp_path, "t-1", "alice")
    key = _keypair(tmp_path)
    seal_task(tmp_path, "t-1", key, "alice")
    # amend after seal -> new revision is unsealed
    review_task(tmp_path, "t-1", "bob", {"outcome": "changed"})
    spec = store.load(tmp_path, "t-1")
    assert spec.state is TaskState.REVIEWED and spec.revision == 2
    rev = json.loads(
        (store.task_dir(tmp_path, "t-1") / "revisions" / "2.json").read_text()
    )
    assert rev["seal_signature_b64"] is None


def test_ready_requires_seal(tmp_path: Path) -> None:
    create_task(tmp_path, _spec())
    review_task(tmp_path, "t-1", "alice")
    with pytest.raises(ContractError, match="AF-TASK-UNSEALED"):
        ready_task(tmp_path, "t-1")


def test_run_direct_recipe_ends_supervised(tmp_path: Path) -> None:
    create_task(tmp_path, _spec())
    review_task(tmp_path, "t-1", "alice")
    seal_task(tmp_path, "t-1", _keypair(tmp_path), "alice")
    record = run_task(tmp_path, "t-1", "af-extractor")
    assert record["terminal"] == "awaiting_supervision"
    assert record["executed_by"] == "af-extractor"
    assert all(s["status"] == "ran" for s in record["steps"])


def test_run_blocked_when_inputs_missing(tmp_path: Path) -> None:
    create_task(tmp_path, _spec(strategy="plan-execute-verify"))
    review_task(tmp_path, "t-1", "alice")
    seal_task(tmp_path, "t-1", _keypair(tmp_path), "alice")
    record = run_task(tmp_path, "t-1", "af-extractor")
    assert record["terminal"] == "blocked"
    assert record["reason"] == "round ended with zero ran steps"


def test_run_with_bound_inputs(tmp_path: Path) -> None:
    fixtures = Path(__file__).resolve().parents[2] / "tests" / "fixtures"
    case_dir = tmp_path / "case"
    analyze_project(
        fixtures / "openapi" / "orders-v1.yaml",
        fixtures / "fastapi_orders",
        None,
        case_dir,
    )
    spec = _spec(
        strategy="test-first",
        inputs=(
            f"project={fixtures / 'fastapi_orders'}",
            f"contract={fixtures / 'openapi' / 'orders-v1.yaml'}",
            f"case={case_dir}",
        ),
    )
    create_task(tmp_path, spec)
    review_task(tmp_path, "t-1", "alice")
    seal_task(tmp_path, "t-1", _keypair(tmp_path), "alice")
    record = run_task(tmp_path, "t-1", "af-synthesizer", now="2026-09-21T00:00:00Z")
    assert record["terminal"] == "awaiting_supervision"
    assert record["calls"] <= 20
    assert all(s["status"] == "ran" for s in record["steps"])


def test_acceptance_needs_distinct_actor(tmp_path: Path) -> None:
    create_task(tmp_path, _spec())
    review_task(tmp_path, "t-1", "alice")
    seal_task(tmp_path, "t-1", _keypair(tmp_path), "alice")
    run_task(tmp_path, "t-1", "af-extractor")
    with pytest.raises(Exception, match="separate from the executor"):
        accept_task(tmp_path, "t-1", "af-extractor")
    record = accept_task(tmp_path, "t-1", "alice", evidence=("runs/0.json",))
    assert record["verdict"] == "accepted"
    assert store.load(tmp_path, "t-1").state is TaskState.ACCEPTED


def test_brief_done_only_after_acceptance(tmp_path: Path) -> None:
    create_task(tmp_path, _spec())
    brief = brief_for_task(tmp_path, "t-1")
    assert brief.status is BriefStatus.DECIDE  # draft -> lifecycle pending
    review_task(tmp_path, "t-1", "alice")
    seal_task(tmp_path, "t-1", _keypair(tmp_path), "alice")
    run_task(tmp_path, "t-1", "af-extractor")
    brief = brief_for_task(tmp_path, "t-1")
    assert brief.status is BriefStatus.DECIDE
    assert brief.human_action is not None
    accept_task(tmp_path, "t-1", "alice", evidence=("runs/0.json",))
    brief = brief_for_task(tmp_path, "t-1")
    assert brief.status is BriefStatus.DONE
    assert brief.proof == ("runs/0.json",)


def test_status_returns_history(tmp_path: Path) -> None:
    create_task(tmp_path, _spec())
    review_task(tmp_path, "t-1", "alice")
    status = task_status(tmp_path, "t-1")
    assert status["task"]["state"] == "reviewed"
    assert len(status["history"]) == 2
