"""Phase 10 §46–§48: Forge Protocol — capabilities, lifecycle, evidence, handoff, health."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.contracts.forge_protocol import ForgeTaskRequest
from apiforge.contracts.task import TaskSpec, TaskState
from apiforge.forge import store
from apiforge.forge.protocol import (
    _load_policy,
    attach_task,
    discover_capabilities,
    health,
    inspect_task,
    prepare_handoff,
    retrieve_evidence,
    retrieve_result,
    submit_task,
)
from apiforge.taskspec import store as taskstore
from apiforge.taskspec.service import create_task as governed_create


def _request(task_id: str = "demo-task", **kwargs: object) -> ForgeTaskRequest:
    fields: dict[str, object] = {"capability_id": "api.analyze", "intent": "demo"}
    fields.update(kwargs)
    return ForgeTaskRequest(task_id=task_id, **fields)  # type: ignore[arg-type]


def _submit(root: Path, task_id: str = "demo-task", **kwargs: object) -> None:
    submit_task(root, _request(task_id, **kwargs))


# --- capabilities ------------------------------------------------------------


def test_capabilities_project_matrix() -> None:
    rows = discover_capabilities()
    assert len(rows) > 0
    assert all(row.capability_id and row.operation for row in rows)
    assert {row.schema for row in rows} == {"apiforge/forge-capability-descriptor/v1"}


# --- submit ------------------------------------------------------------------


def test_submit_persists_accepted(tmp_path: Path) -> None:
    status = submit_task(tmp_path, _request())
    assert status.state == "accepted"
    assert (store.task_dir(tmp_path, "demo-task") / "request.json").is_file()
    assert (store.task_dir(tmp_path, "demo-task") / "events.jsonl").is_file()


def test_submit_unknown_capability_refuses(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="AF-FORGE-CAPABILITY-UNKNOWN"):
        submit_task(tmp_path, _request(capability_id="no.such.capability"))
    assert store.task_ids(tmp_path) == []  # refused submissions persist nothing


def test_submit_risk_gate(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="AF-FORGE-RISK-GATE"):
        submit_task(tmp_path, _request(risk="external_mutation"))
    status = submit_task(tmp_path, _request(risk="external_mutation"), acknowledge_risk=True)
    assert status.state == "accepted"


def test_submit_existing_refuses(tmp_path: Path) -> None:
    _submit(tmp_path)
    with pytest.raises(ContractError, match="AF-FORGE-TASK-EXISTS"):
        _submit(tmp_path)


def test_bad_task_id_refuses() -> None:
    with pytest.raises(Exception, match="pattern"):
        _request("BAD_ID")


def test_bad_policy_refuses(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("engine: only\n", encoding="utf-8")
    with pytest.raises(ContractError, match="AF-FORGE-POLICY"):
        _load_policy(bad)


# --- attach + inspect --------------------------------------------------------


def _governed(root: Path, task_id: str = "gov-task") -> str:
    governed_create(root, TaskSpec(id=task_id, outcome="governed outcome"))
    return task_id


def test_attach_links_and_projects(tmp_path: Path) -> None:
    _submit(tmp_path)
    governed = _governed(tmp_path)
    status = attach_task(tmp_path, "demo-task", governed)
    assert status.governed_task_id == governed
    assert status.governed_state == "draft"
    assert status.state == "in_progress"
    # live projection follows the governed lifecycle
    spec = taskstore.load(tmp_path, governed).model_copy(update={"state": TaskState.ACCEPTED})
    taskstore.write_spec(taskstore.task_dir(tmp_path, governed), spec)
    assert inspect_task(tmp_path, "demo-task").state == "completed"


def test_attach_missing_governed_refuses(tmp_path: Path) -> None:
    _submit(tmp_path)
    with pytest.raises(ContractError, match="AF-TASK-NOT-FOUND"):
        attach_task(tmp_path, "demo-task", "no-such-task")


def test_attach_terminal_refuses(tmp_path: Path) -> None:
    _submit(tmp_path)
    governed = _governed(tmp_path)
    spec = taskstore.load(tmp_path, governed).model_copy(update={"state": TaskState.ACCEPTED})
    taskstore.write_spec(taskstore.task_dir(tmp_path, governed), spec)
    attach_task(tmp_path, "demo-task", governed)
    with pytest.raises(ContractError, match="AF-FORGE-STATE"):
        attach_task(tmp_path, "demo-task", governed)


def test_inspect_missing_task_refuses(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="AF-FORGE-TASK-NOT-FOUND"):
        inspect_task(tmp_path, "ghost-task")


def test_inspect_broken_link_unresolved(tmp_path: Path) -> None:
    _submit(tmp_path)
    governed = _governed(tmp_path)
    attach_task(tmp_path, "demo-task", governed)
    import shutil

    shutil.rmtree(taskstore.task_dir(tmp_path, governed))
    status = inspect_task(tmp_path, "demo-task")
    assert status.state == "unresolved"
    assert any("link broken" in item for item in status.unresolved)


# --- result ------------------------------------------------------------------


def test_result_without_link_unresolved(tmp_path: Path) -> None:
    _submit(tmp_path)
    result = retrieve_result(tmp_path, "demo-task")
    assert result.status == "unresolved"
    assert any("attach" in gap for gap in result.gaps)


def test_result_maps_governed_brief(tmp_path: Path) -> None:
    _submit(tmp_path)
    governed = _governed(tmp_path)
    attach_task(tmp_path, "demo-task", governed)
    result = retrieve_result(tmp_path, "demo-task")
    # governed task is draft -> brief DECIDE -> forge review
    assert result.status == "review"
    assert result.payload["governed_task_id"] == governed
    spec = taskstore.load(tmp_path, governed).model_copy(update={"state": TaskState.ACCEPTED})
    taskstore.write_spec(taskstore.task_dir(tmp_path, governed), spec)
    taskstore.record_event(
        tmp_path, governed, {"event": "->accepted", "by": "reviewer", "evidence": ["e1"]}
    )
    result2 = retrieve_result(tmp_path, "demo-task")
    assert result2.status == "ok"
    assert result2.evidence


# --- evidence ----------------------------------------------------------------


def test_evidence_bundle_content_addressed(tmp_path: Path) -> None:
    _submit(tmp_path)
    governed = _governed(tmp_path)
    attach_task(tmp_path, "demo-task", governed)
    bundle = retrieve_evidence(tmp_path, "demo-task")
    kinds = {a.kind for a in bundle.artifacts}
    assert {"request", "status", "ledger", "governed"} <= kinds
    assert all(len(a.sha256) == 64 for a in bundle.artifacts)
    assert bundle.unresolved == ()


def test_evidence_without_link_names_gap(tmp_path: Path) -> None:
    _submit(tmp_path)
    bundle = retrieve_evidence(tmp_path, "demo-task")
    assert any("no governed task attached" in item for item in bundle.unresolved)


# --- handoff -----------------------------------------------------------------


def test_handoff_prepared_bundle(tmp_path: Path) -> None:
    _submit(tmp_path)
    governed = _governed(tmp_path)
    attach_task(tmp_path, "demo-task", governed)
    handoff = prepare_handoff(
        tmp_path, "demo-task", "spark-forge", context_refs=("ctx://case/demo",)
    )
    assert handoff.delivery == "prepared"
    assert handoff.from_engine == "api-forge"
    assert handoff.to_engine == "spark-forge"
    assert handoff.request.task_id == "demo-task"
    assert handoff.status is not None and handoff.status.state == "in_progress"
    assert len(handoff.evidence_refs) > 0
    assert any("human/transport" in item for item in handoff.unresolved)
    persisted = store.load_handoff(tmp_path, handoff.handoff_id)
    assert persisted.handoff_id == handoff.handoff_id


def test_handoff_unknown_engine_refuses(tmp_path: Path) -> None:
    _submit(tmp_path)
    with pytest.raises(ContractError, match="AF-FORGE-ENGINE-UNKNOWN"):
        prepare_handoff(tmp_path, "demo-task", "other-engine")


def test_handoff_idempotent_id_refuses(tmp_path: Path) -> None:
    _submit(tmp_path)
    prepare_handoff(tmp_path, "demo-task", "spark-forge")
    with pytest.raises(ContractError, match="AF-FORGE-HANDOFF-EXISTS"):
        prepare_handoff(tmp_path, "demo-task", "spark-forge")


# --- health ------------------------------------------------------------------


def test_health_counts_and_degrades(tmp_path: Path) -> None:
    report = health(tmp_path)
    assert report.engine == "api-forge"
    assert report.protocol_version == "forge-protocol/v1"
    assert report.state == "ok"
    _submit(tmp_path)
    report = health(tmp_path)
    assert report.tasks_by_state == {"accepted": 1}
    # corrupt a stored row -> degraded, not silent
    (store.task_dir(tmp_path, "demo-task") / "status.json").write_text("{bad", encoding="utf-8")
    report = health(tmp_path)
    assert report.state == "degraded"
    assert report.unresolved


def test_forged_task_request_frozen_inputs() -> None:
    req = _request(inputs={"contract": "orders.yaml"})
    dumped = json.loads(req.model_dump_json())
    assert dumped["inputs"] == {"contract": "orders.yaml"}
