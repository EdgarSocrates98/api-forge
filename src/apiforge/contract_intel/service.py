"""Deterministic contract analysis and no-network API twin simulation."""

from __future__ import annotations

from pathlib import Path

from apiforge.contract_intel.models import (
    ContractImpact,
    ContractProtocol,
    ImpactVerdict,
    TwinPlan,
    TwinScenario,
    TwinSimulation,
)
from apiforge.core.ids import stable_id
from apiforge.grpc.compatibility import compare as compare_grpc
from apiforge.grpc.source import load_source
from apiforge.openapi.diff import diff_contracts
from apiforge.openapi.loader import load_openapi

_DEFAULT_SCENARIOS = (
    ("happy-path", "happy path", 200, "success"),
    ("validation-error", "validation error", 422, "invalid input rejected"),
    ("auth-denied", "authentication denied", 401, "request rejected at auth boundary"),
    ("dependency-timeout", "dependency timeout", 504, "timeout handled without hanging"),
    ("dependency-5xx", "dependency 5xx", 502, "downstream failure isolated"),
    ("rate-limit", "rate limit", 429, "traffic constrained by policy"),
    ("idempotent-retry", "idempotent retry", 200, "duplicate mutation does not duplicate effect"),
    ("contract-mismatch", "contract mismatch", 500, "mismatch is surfaced as review evidence"),
)


def _impact_from_openapi(baseline: Path, candidate: Path) -> ContractImpact:
    old, new = load_openapi(baseline), load_openapi(candidate)
    changes = diff_contracts(old, new)
    breaking = tuple(item for item in changes if item.breaking)
    review = tuple(
        item for item in changes if not item.breaking and item.status.value == "unresolved"
    )
    verdict = (
        ImpactVerdict.BREAKING
        if breaking
        else ImpactVerdict.REVIEW
        if review
        else ImpactVerdict.COMPATIBLE
    )
    refs = tuple(sorted({f"{item.method.upper()} {item.path}" for item in changes if item.method}))
    return ContractImpact(
        protocol=ContractProtocol.OPENAPI,
        verdict=verdict,
        baseline_digest=old.sha256,
        candidate_digest=new.sha256,
        breaking_count=len(breaking),
        review_count=len(review),
        affected_refs=refs,
        changes=tuple(item.model_dump(mode="json") for item in changes),
        evidence=(f"baseline:{baseline}:{old.sha256}", f"candidate:{candidate}:{new.sha256}"),
    )


def _impact_from_grpc(baseline: Path, candidate: Path) -> ContractImpact:
    old, new = load_source(baseline), load_source(candidate)
    report = compare_grpc(old, new)
    breaking = tuple(item for item in report.diagnostics if item.severity.value == "breaking")
    review = tuple(item for item in report.diagnostics if item.severity.value == "review")
    verdict = (
        ImpactVerdict.BREAKING
        if report.verdict == "breaking"
        else ImpactVerdict.REVIEW
        if report.verdict == "review"
        else ImpactVerdict.COMPATIBLE
    )
    return ContractImpact(
        protocol=ContractProtocol.GRPC,
        verdict=verdict,
        baseline_digest=report.baseline_digest,
        candidate_digest=report.candidate_digest,
        breaking_count=len(breaking),
        review_count=len(review),
        affected_refs=tuple(sorted({item.path for item in report.diagnostics if item.path})),
        changes=tuple(item.model_dump(mode="json") for item in report.diagnostics),
        evidence=tuple(old.provenance) + tuple(new.provenance),
    )


def analyze_contract(protocol: ContractProtocol, baseline: Path, candidate: Path) -> ContractImpact:
    """Analyze supported contracts; unsupported protocols remain explicit."""
    if protocol == ContractProtocol.OPENAPI:
        return _impact_from_openapi(baseline, candidate)
    if protocol == ContractProtocol.GRPC:
        return _impact_from_grpc(baseline, candidate)
    raise ValueError(f"AF-CONTRACT-INTEL-UNSUPPORTED: {protocol.value} requires an adapter")


def build_twin_plan(
    contract: Path, protocol: ContractProtocol, dependencies: tuple[str, ...] = ()
) -> TwinPlan:
    """Build a closed offline scenario plan. It never starts a server or calls the network."""
    if protocol == ContractProtocol.OPENAPI:
        document = load_openapi(contract)
        operations = tuple(f"{item.method.upper()} {item.path}" for item in document.operations)
        digest = document.sha256
    elif protocol == ContractProtocol.GRPC:
        ir = load_source(contract)
        operations = tuple(rpc.full_name for service in ir.services for rpc in service.rpcs)
        digest = ir.source_sha256
    else:
        raise ValueError(f"AF-TWIN-UNSUPPORTED: {protocol.value} requires an adapter")
    target = operations[0] if operations else "contract"
    scenarios = tuple(
        TwinScenario(
            scenario_id=scenario_id,
            name=name,
            target=target,
            dependency_failures=("timeout",)
            if scenario_id == "dependency-timeout"
            else ("http-5xx",)
            if scenario_id == "dependency-5xx"
            else (),
            status_override=status,
            expected_status=status,
            expected_outcome=outcome,
        )
        for scenario_id, name, status, outcome in _DEFAULT_SCENARIOS
    )
    return TwinPlan(
        protocol=protocol,
        contract_path=str(contract),
        contract_digest=digest,
        operations=operations,
        dependencies=tuple(sorted(set(dependencies))),
        scenarios=scenarios,
        proof_axes=("contract", "failure-isolation", "idempotency", "security", "no-network"),
    )


def simulate_twin(plan: TwinPlan, scenario_id: str) -> TwinSimulation:
    """Simulate one scenario from data only; network_called is always false by design."""
    scenario = next((item for item in plan.scenarios if item.scenario_id == scenario_id), None)
    if scenario is None:
        raise ValueError(f"AF-TWIN-SCENARIO-UNKNOWN: {scenario_id}")
    plan_digest = stable_id("twin-plan", plan.model_dump(mode="json"))
    return TwinSimulation(
        plan_digest=plan_digest,
        scenario_id=scenario.scenario_id,
        status=scenario.status_override or scenario.expected_status,
        outcome=scenario.expected_outcome,
        latency_ms=scenario.latency_ms,
        dependency_failures=scenario.dependency_failures,
        evidence=(
            f"plan:{plan.contract_path}:{plan.contract_digest}",
            "mode:offline",
            "network_called:false",
        ),
    )
