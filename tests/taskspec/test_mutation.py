"""Mutation recipes — `build endpoint` inside a sealed task, policy-gated."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.task import TaskSpec
from apiforge.dispatch.runner import DispatchContext, dispatch_step
from apiforge.policy.loader import load_policy_from_text
from apiforge.taskspec.runner import run_task
from apiforge.taskspec.service import create_task, review_task, seal_task

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures"


def _keypair(tmp_path: Path) -> Path:
    from apiforge.report.keys import generate_keypair

    generate_keypair(tmp_path / "keys", "sealer")
    return tmp_path / "keys" / "sealer.pem"


def _project(tmp_path: Path) -> Path:
    proj = tmp_path / "proj"
    (proj / "src" / "main" / "java").mkdir(parents=True)
    (proj / "pom.xml").write_text("<project/>\n", encoding="utf-8")
    return proj


def _sealed_task(tmp_path: Path, **kw: object) -> None:
    create_task(tmp_path, TaskSpec.model_validate({
        "id": "t-build", "outcome": "build createOrder", **kw,
    }))
    review_task(tmp_path, "t-build", "alice")
    seal_task(tmp_path, "t-build", _keypair(tmp_path), "alice")


def test_dispatch_refuses_mutation_without_gate(tmp_path: Path) -> None:
    ctx = DispatchContext(
        case=tmp_path,
        project=_project(tmp_path),
        contract=FIXTURES / "openapi" / "orders-v1.yaml",
        operation_id="createOrder",
    )
    entry = dispatch_step("build endpoint", ctx)
    assert entry["status"] == "refused"
    assert "AF-TASK-MUTATION-GATED" in str(entry["reason"])


def test_build_endpoint_recipe_runs_in_sandbox_only(tmp_path: Path) -> None:
    from apiforge.application.analyze import analyze_project

    proj = _project(tmp_path)
    case_dir = tmp_path / "case"
    analyze_project(
        FIXTURES / "openapi" / "orders-v1.yaml",
        FIXTURES / "fastapi_orders",
        None,
        case_dir,
    )
    _sealed_task(
        tmp_path,
        strategy="build-endpoint",
        writable_paths=(".apiforge",),
        inputs=(
            f"contract={FIXTURES / 'openapi' / 'orders-v1.yaml'}",
            f"project={proj}",
            f"case={case_dir}",
            "operation_id=createOrder",
        ),
    )
    record = run_task(
        tmp_path, "t-build", "af-extractor", now="2026-09-21T00:00:00Z"
    )
    assert record["terminal"] == "awaiting_supervision", record["steps"]
    build_step = next(s for s in record["steps"] if s["verb"] == "build endpoint")
    assert build_step["status"] == "ran"
    assert build_step["policy_decision"]["outcome"] == "allow"
    # writes land in the sandbox, never the main tree
    assert not (proj / "src/main/java/com/apiforge").exists()


def test_mutation_refused_without_writable_scope(tmp_path: Path) -> None:
    _sealed_task(
        tmp_path,
        strategy="build-endpoint",
        inputs=(
            f"contract={FIXTURES / 'openapi' / 'orders-v1.yaml'}",
            f"project={_project(tmp_path)}",
            "operation_id=createOrder",
        ),
    )
    record = run_task(tmp_path, "t-build", "af-extractor")
    assert record["terminal"] == "parked"
    step = next(s for s in record["steps"] if s["verb"] == "build endpoint")
    assert step["status"] == "refused"
    assert "writable_paths" in str(step["reason"])


def test_mutation_refused_when_policy_denies(tmp_path: Path, monkeypatch) -> None:
    deny = load_policy_from_text(
        "version: 1\n"
        "defaults: {read_only: allow, local_reversible: deny, sensitive: gate,"
        " external_mutation: gate, destructive: gate, irreversible: deny}\n"
    )
    monkeypatch.setattr("apiforge.policy.loader.load_policy", lambda p=None: deny)
    _sealed_task(
        tmp_path,
        strategy="build-endpoint",
        writable_paths=(".apiforge",),
        inputs=(
            f"contract={FIXTURES / 'openapi' / 'orders-v1.yaml'}",
            f"project={_project(tmp_path)}",
            "operation_id=createOrder",
        ),
    )
    record = run_task(tmp_path, "t-build", "af-extractor")
    assert record["terminal"] == "parked"
    step = next(s for s in record["steps"] if s["verb"] == "build endpoint")
    assert step["status"] == "refused"
    assert step["policy_decision"]["outcome"] == "deny"


def test_missing_operation_id_is_pending_not_run(tmp_path: Path) -> None:
    _sealed_task(
        tmp_path,
        strategy="build-endpoint",
        writable_paths=(".apiforge",),
        inputs=(
            f"contract={FIXTURES / 'openapi' / 'orders-v1.yaml'}",
            f"project={_project(tmp_path)}",
        ),
    )
    record = run_task(tmp_path, "t-build", "af-extractor")
    step = next(s for s in record["steps"] if s["verb"] == "build endpoint")
    assert step["status"] == "pending"
    assert "operation_id" in step["missing"]
