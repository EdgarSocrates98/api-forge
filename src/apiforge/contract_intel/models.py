"""Provider-neutral outputs for contract change impact and API twin planning."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from apiforge.contracts.base import VersionedContract


class ContractProtocol(StrEnum):
    OPENAPI = "openapi"
    GRPC = "grpc"
    ASYNCAPI = "asyncapi"
    GRAPHQL = "graphql"


class ImpactVerdict(StrEnum):
    COMPATIBLE = "compatible"
    REVIEW = "review"
    BREAKING = "breaking"
    INCONCLUSIVE = "inconclusive"


class ContractImpact(VersionedContract):
    protocol: ContractProtocol
    verdict: ImpactVerdict
    baseline_digest: str
    candidate_digest: str
    breaking_count: int = Field(ge=0)
    review_count: int = Field(ge=0)
    affected_refs: tuple[str, ...] = ()
    changes: tuple[dict[str, object], ...] = ()
    evidence: tuple[str, ...] = ()


class TwinScenario(VersionedContract):
    scenario_id: str
    name: str
    target: str
    dependency_failures: tuple[str, ...] = ()
    latency_ms: int = Field(default=0, ge=0)
    status_override: int | None = Field(default=None, ge=100, le=599)
    expected_status: int = Field(default=200, ge=100, le=599)
    expected_outcome: str


class TwinPlan(VersionedContract):
    protocol: ContractProtocol
    contract_path: str
    contract_digest: str
    operations: tuple[str, ...]
    dependencies: tuple[str, ...]
    scenarios: tuple[TwinScenario, ...]
    proof_axes: tuple[str, ...]
    network_allowed: bool = False
    execution_status: str = "plan_only"


class TwinSimulation(VersionedContract):
    plan_digest: str
    scenario_id: str
    status: int
    outcome: str
    latency_ms: int = Field(ge=0)
    dependency_failures: tuple[str, ...] = ()
    network_called: bool = False
    evidence: tuple[str, ...] = ()
