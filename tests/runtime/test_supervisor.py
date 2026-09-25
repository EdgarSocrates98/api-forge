from pathlib import Path

from apiforge.capabilities.registry import load_capabilities
from apiforge.contracts.platform import CapabilityRequest
from apiforge.integrations.gateway import IntegrationGateway, StaticIntegrationAdapter
from apiforge.runtime.control import ControlPlane
from apiforge.runtime.runner import run_runtime
from tests.runtime.test_runtime import make_task


def test_supervisor_returns_a_terminal_review_boundary(tmp_path: Path) -> None:
    make_task(tmp_path)
    result = run_runtime(tmp_path, "evolve-orders-api")
    assert result["status"] in {"REVIEW", "BLOCKED", "DONE"}


def test_supervisor_persists_control_authority(tmp_path: Path) -> None:
    make_task(tmp_path)
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-23T12:00:00+00:00")
    run = result["run"]
    assert isinstance(run, dict)
    control_id = run["control_run_id"]
    control = ControlPlane(tmp_path).get(str(control_id))
    assert control.status == "awaiting_review"
    assert all(step.status == "succeeded" for step in control.steps)


def test_supervisor_persists_routing_trace(tmp_path: Path) -> None:
    make_task(tmp_path)
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-23T12:00:00+00:00")
    routing = Path(str(result["run_dir"])) / "routing.json"
    assert routing.is_file()
    payload = routing.read_text(encoding="utf-8")
    assert "fallback_order" in payload
    assert "unresolved" in payload


def test_external_mutation_requires_policy_approval_and_rollback() -> None:
    record = next(item for item in load_capabilities() if item.capability_id == "external.apply")
    gateway = IntegrationGateway((StaticIntegrationAdapter("fake", (record,)),))
    request = CapabilityRequest(
        capability_id="external.apply",
        intent="apply a provider change",
        surface="cli",
        action="apply",
    )
    result = gateway.execute(request, adapter="fake", allow_external_mutation=True)
    assert result.status == "blocked"
    assert result.error_code == "AF-INTEGRATION-GATE"
