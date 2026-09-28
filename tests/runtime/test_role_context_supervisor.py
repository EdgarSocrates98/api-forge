import json
from pathlib import Path

import apiforge.runtime.shadow as shadow_module
import apiforge.runtime.supervisor as supervisor_module
from apiforge.contracts.task import TaskRisk, TaskSize, TaskSpec, TaskState
from apiforge.runtime.adapters import FakeModelAdapter
from apiforge.runtime.runner import run_runtime
from apiforge.taskspec.store import create
from tests.context.gateway_support import analyzed_root

NOW = "2026-09-28T12:00:00+00:00"
TASK = "evolve-payments"


def _task(root: Path, *, target: bool = True) -> None:
    inputs = [f"project={root / 'proj'}"]
    if target:
        inputs.append("target=POST /payments")
    create(
        root,
        TaskSpec(
            id=TASK,
            outcome="make POST /payments idempotent",
            size=TaskSize.M,
            inputs=tuple(inputs),
            expected_proofs=("specialist artifact",),
            acceptance_criteria=("findings are evidence bound",),
            rollback="discard local run artifacts",
            risk=TaskRisk.READ_ONLY,
            state=TaskState.SEALED,
            revision=1,
            budgets={"max_calls": 20},
        ),
    )


def _run(root: Path, adapter: FakeModelAdapter, profile: str = "balanced"):
    return run_runtime(root, TASK, adapter=adapter, now=NOW, profile=profile)


def test_each_invocation_gets_its_role_context(tmp_path: Path) -> None:
    root = analyzed_root(tmp_path, "fastapi")
    _task(root)
    adapter = FakeModelAdapter()
    result = _run(root, adapter)
    plan = json.loads((Path(str(result["run_dir"])) / "role-context.json").read_text("utf-8"))
    assert plan["capsule_id"] and plan["target"] == "POST /payments"
    by_capability = {call.capability: call for call in adapter.calls}
    primary = by_capability["api-contract-review"]
    assert primary.context_class == "focused" and primary.context_refs
    reviewer = by_capability["task-review"]
    assert reviewer.context_class == "evidence_plus_delta"
    assert len(reviewer.context_refs) <= len(primary.context_refs)
    summary = result["role_context"]
    assert summary["total_bytes"] <= summary["naive_bytes"]
    ledger = (root / ".apiforge" / "economy.jsonl").read_text("utf-8")
    assert "runtime role:specialist" in ledger


def test_without_target_roles_get_no_capsule(tmp_path: Path) -> None:
    root = analyzed_root(tmp_path, "fastapi")
    _task(root, target=False)
    adapter = FakeModelAdapter()
    result = _run(root, adapter)
    assert result["role_context"]["unresolved"] == ["capsule-unavailable:no-target"]
    assert all(call.context_refs == () for call in adapter.calls)


def test_shadow_runs_outside_the_result(tmp_path: Path, monkeypatch) -> None:
    root = analyzed_root(tmp_path, "fastapi")
    _task(root)
    baseline = _run(root, FakeModelAdapter())
    original = supervisor_module.build_routing_plan

    def with_challenger(*args, **kwargs):
        plan = original(*args, **kwargs)
        return plan.model_copy(
            update={"challenger_order": ("api-architecture-review",), "challenger_slots": 1}
        )

    monkeypatch.setattr(supervisor_module, "build_routing_plan", with_challenger)
    monkeypatch.setattr(shadow_module, "sampled", lambda run_id, share: True)
    adapter = FakeModelAdapter()
    shadowed = _run(root, adapter)
    decision = shadowed["shadow"]
    assert decision["executed"] is True and decision["calls"] == 1
    assert decision["challenger"] == "api-architecture-review"
    assert any(call.capability == "api-architecture-review" for call in adapter.calls)
    assert shadowed["status"] == baseline["status"]
    assert len(shadowed["artifacts"]) == len(baseline["artifacts"])
    assert (Path(str(shadowed["run_dir"])) / "shadow-api-architecture-review.json").is_file()
