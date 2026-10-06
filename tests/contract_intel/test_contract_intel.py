from pathlib import Path

import pytest

from apiforge.contract_intel import (
    ContractProtocol,
    ImpactVerdict,
    analyze_contract,
    build_twin_plan,
    simulate_twin,
)

ROOT = Path(__file__).parents[2]
OPENAPI_V1 = ROOT / "tests/fixtures/openapi/orders-v1.yaml"
OPENAPI_V2 = ROOT / "tests/fixtures/openapi/orders-v2-breaking.yaml"
GRPC_V1 = ROOT / "tests/fixtures/grpc/orders.proto"
GRPC_V2 = ROOT / "tests/fixtures/grpc/orders-breaking.proto"


def test_openapi_impact_is_unified_and_breaking() -> None:
    result = analyze_contract(ContractProtocol.OPENAPI, OPENAPI_V1, OPENAPI_V2)

    assert result.verdict is ImpactVerdict.BREAKING
    assert result.breaking_count > 0
    assert result.baseline_digest != result.candidate_digest


def test_grpc_impact_is_unified() -> None:
    result = analyze_contract(ContractProtocol.GRPC, GRPC_V1, GRPC_V2)

    assert result.protocol is ContractProtocol.GRPC
    assert result.verdict is ImpactVerdict.BREAKING
    assert result.affected_refs


def test_twin_is_plan_only_and_simulation_is_deterministic() -> None:
    plan = build_twin_plan(OPENAPI_V1, ContractProtocol.OPENAPI, ("orders-db", "redis"))

    assert plan.network_allowed is False
    assert plan.execution_status == "plan_only"
    assert len(plan.scenarios) == 8
    first = simulate_twin(plan, "dependency-timeout")
    second = simulate_twin(plan, "dependency-timeout")
    assert first == second
    assert first.status == 504
    assert first.network_called is False
    assert first.dependency_failures == ("timeout",)


def test_twin_rejects_unknown_scenario() -> None:
    plan = build_twin_plan(OPENAPI_V1, ContractProtocol.OPENAPI)

    with pytest.raises(ValueError, match="AF-TWIN-SCENARIO-UNKNOWN"):
        simulate_twin(plan, "not-declared")
