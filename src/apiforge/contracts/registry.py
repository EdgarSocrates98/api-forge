"""The contract registry: ``<Name>/v1`` -> model class, introspectable."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from apiforge.contracts.base import ContractError
from apiforge.contracts.core import (
    ActionPlan,
    ActionStep,
    ArtifactRef,
    Decision,
    Verification,
)
from apiforge.contracts.graph import GraphEdge, GraphExport, GraphNode
from apiforge.contracts.stubs import (
    DataAccessIR,
    PerformanceRun,
    RuntimeMatrix,
    TelemetryEvent,
)
from apiforge.contracts.task import (
    AcceptanceRecord,
    CapabilityProof,
    OutcomeBrief,
    TaskHandoff,
    TaskPlan,
    TaskRevision,
    TaskSpec,
)
from apiforge.core.models import Fact, Finding
from apiforge.evidence.models import Receipt

CONTRACTS: dict[str, type[BaseModel]] = {
    "ArtifactRef/v1": ArtifactRef,
    "Fact/v1": Fact,
    "Finding/v1": Finding,
    "Receipt/v1": Receipt,
    "Decision/v1": Decision,
    "ActionPlan/v1": ActionPlan,
    "ActionStep/v1": ActionStep,
    "Verification/v1": Verification,
    "TaskSpec/v1": TaskSpec,
    "TaskRevision/v1": TaskRevision,
    "TaskPlan/v1": TaskPlan,
    "TaskHandoff/v1": TaskHandoff,
    "AcceptanceRecord/v1": AcceptanceRecord,
    "CapabilityProof/v1": CapabilityProof,
    "OutcomeBrief/v1": OutcomeBrief,
    "GraphNode/v1": GraphNode,
    "GraphEdge/v1": GraphEdge,
    "GraphExport/v1": GraphExport,
    "TelemetryEvent/v1": TelemetryEvent,
    "PerformanceRun/v1": PerformanceRun,
    "DataAccessIR/v1": DataAccessIR,
    "RuntimeMatrix/v1": RuntimeMatrix,
}


def contract_names() -> list[str]:
    return sorted(CONTRACTS)


def contract_schema(name: str) -> dict[str, Any]:
    """The JSON schema of a registered contract — unknown names are refused."""
    model = CONTRACTS.get(name)
    if model is None:
        raise ContractError(
            "AF-CONTRACTS-UNKNOWN",
            f"no contract {name!r}; known: {contract_names()}",
        )
    return model.model_json_schema()
