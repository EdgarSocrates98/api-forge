from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.contracts.task import TaskRisk, TaskSize, TaskSpec, TaskState
from apiforge.runtime.adapters import FakeModelAdapter
from apiforge.runtime.runner import run_runtime, runtime_status
from apiforge.taskspec.store import create


def make_task(root: Path, *, risk: TaskRisk = TaskRisk.READ_ONLY) -> TaskSpec:
    project = root / "project"
    project.mkdir()
    (project / "openapi.yaml").write_text("openapi: 3.0.0\n", encoding="utf-8")
    spec = TaskSpec(
        id="evolve-orders-api",
        outcome="produce a reviewed API evolution plan",
        size=TaskSize.M,
        inputs=(f"project={project}",),
        expected_proofs=("specialist artifact",),
        acceptance_criteria=("all findings are evidence bound",),
        rollback="discard local run artifacts",
        risk=risk,
        state=TaskState.SEALED,
        revision=1,
    )
    return create(root, spec)


def test_runtime_executes_fake_adapter_and_persists_replay(tmp_path: Path) -> None:
    make_task(tmp_path)
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-22T12:00:00+00:00")

    assert result["status"] == "REVIEW"
    run = result["run"]
    assert isinstance(run, dict)
    assert run["task_id"] == "evolve-orders-api"
    run_dir = Path(str(result["run_dir"]))
    assert (run_dir / "run.json").is_file()
    assert (run_dir / "events.jsonl").is_file()
    assert (run_dir / "replay.json").is_file()
    assert runtime_status(tmp_path, "evolve-orders-api")["found"] is True


def test_runtime_opens_debate_for_conflicting_recommendations(tmp_path: Path) -> None:
    make_task(tmp_path)
    adapter = FakeModelAdapter(
        {
            "api-contract-review": {"recommendation": "keep", "confidence": 0.8},
            "api-security-review": {"recommendation": "replace", "confidence": 0.8},
        }
    )

    result = run_runtime(tmp_path, "evolve-orders-api", adapter=adapter, now="2026-09-22T12:00:00+00:00")

    assert result["debate"]["opened"] is True
    assert "conflicting_evidence" in result["debate"]["reasons"]


def test_runtime_blocks_invalid_task_before_adapter(tmp_path: Path) -> None:
    spec = TaskSpec(
        id="invalid-task",
        outcome="missing proof",
        state=TaskState.DRAFT,
    )
    create(tmp_path, spec)
    adapter = FakeModelAdapter()

    result = run_runtime(tmp_path, "invalid-task", adapter=adapter)

    assert result["status"] == "BLOCKED"
    assert adapter.calls == []


@pytest.mark.parametrize("payload", [{"facts": ["x"]}, {"unresolved": ["unknown"]}])
def test_fake_adapter_output_is_json_serializable(payload: dict[str, object]) -> None:
    response = __import__("asyncio").run(
        FakeModelAdapter({"api-contract-review": payload}).invoke(
            __import__("apiforge.runtime.adapters", fromlist=["AgentRequest"]).AgentRequest(
                invocation_id="i",
                agent="a",
                capability="api-contract-review",
                prompt="p",
                output_contract="AgentArtifact/v1",
            )
        )
    )
    assert json.dumps(dict(response.output))
