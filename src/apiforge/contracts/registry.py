"""The contract registry: ``<Name>/v1`` -> model class, introspectable."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from apiforge.contracts.agentic import (
    AgentArtifact,
    AgenticPolicy,
    AgenticRun,
    AgentInvocation,
    ApprovalGate,
    DecisionRecord,
    HandoffRecord,
    TrajectoryEvent,
)
from apiforge.contracts.base import ContractError
from apiforge.contracts.core import (
    ActionPlan,
    ActionStep,
    ArtifactRef,
    Decision,
    Verification,
)
from apiforge.contracts.graph import GraphEdge, GraphExport, GraphNode
from apiforge.contracts.observability import (
    Capability,
    IntentDiff,
    ObservabilityFinding,
    ObservationSnapshot,
    OperationReceipt,
    SignalSummary,
    SLODefinition,
    SLOResult,
    TelemetryRecord,
    VendorIntent,
)
from apiforge.contracts.stubs import (
    DataAccessIR,
    PerformanceRun,
    RuntimeMatrix,
    TelemetryEvent,
    TestRecord,
    WorkloadProfile,
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
from apiforge.contracts.verification import (
    HoldoutRecord,
    VerificationCheck,
    VerificationRecord,
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
    "WorkloadProfile/v1": WorkloadProfile,
    "TestRecord/v1": TestRecord,
    "VerificationRecord/v1": VerificationRecord,
    "VerificationCheck/v1": VerificationCheck,
    "HoldoutRecord/v1": HoldoutRecord,
    "AgenticRun/v1": AgenticRun,
    "AgenticRuntime/v1": AgenticRun,
    "AgenticPolicy/v1": AgenticPolicy,
    "AgentInvocation/v1": AgentInvocation,
    "AgentArtifact/v1": AgentArtifact,
    "HandoffRecord/v1": HandoffRecord,
    "DecisionRecord/v1": DecisionRecord,
    "ApprovalGate/v1": ApprovalGate,
    "TrajectoryEvent/v1": TrajectoryEvent,
    "TelemetryRecord/v1": TelemetryRecord,
    "ObservationSnapshot/v1": ObservationSnapshot,
    "SLODefinition/v1": SLODefinition,
    "SignalSummary/v1": SignalSummary,
    "SLOResult/v1": SLOResult,
    "Capability/v1": Capability,
    "VendorIntent/v1": VendorIntent,
    "IntentDiff/v1": IntentDiff,
    "OperationReceipt/v1": OperationReceipt,
    "ObservabilityFinding/v1": ObservabilityFinding,
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
