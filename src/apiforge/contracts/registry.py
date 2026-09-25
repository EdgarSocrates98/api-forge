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
    RuntimeReview,
    TrajectoryEvent,
)
from apiforge.contracts.base import ContractError
from apiforge.contracts.context import ContextScope
from apiforge.contracts.core import (
    ActionPlan,
    ActionStep,
    ArtifactRef,
    Decision,
    Verification,
)
from apiforge.contracts.devin import DevinCheck, DevinCliProbe, DevinLaunch, DevinPayload
from apiforge.contracts.distribution import DistributionDoctor
from apiforge.contracts.evidence import EvidenceRef
from apiforge.contracts.graph import GraphEdge, GraphExport, GraphNode
from apiforge.contracts.grpc import (
    GrpcArtifact,
    GrpcCapability,
    GrpcCodegenRequest,
    GrpcCodegenResult,
    GrpcCompatibilityReport,
    GrpcDiagnostic,
    GrpcGatewayProjection,
    GrpcGatewayRequest,
    GrpcIR,
    GrpcMessage,
    GrpcPerformanceReport,
    GrpcPerformanceRun,
    GrpcPlan,
    GrpcRpc,
    GrpcRuntimePolicy,
    GrpcSecurityReport,
    GrpcService,
    GrpcVerification,
)
from apiforge.contracts.integration import (
    ExternalReadReceipt,
    ExternalReadRequest,
    ExternalReadResult,
    GitHubPrReceipt,
)
from apiforge.contracts.knowledge import ExpertisePack
from apiforge.contracts.observability import (
    Capability,
    CircuitBreakerEvent,
    CircuitBreakerMetrics,
    CircuitBreakerPolicy,
    CircuitMetricsExportReceipt,
    HostExportBinding,
    IntentDiff,
    ObservabilityExportReadiness,
    ObservabilityFinding,
    ObservationSnapshot,
    OperationReceipt,
    ReadRetryPolicy,
    ReadSafetyPolicy,
    SignalSummary,
    SLODefinition,
    SLOResult,
    TelemetryRecord,
    VendorIntent,
)
from apiforge.contracts.platform import (
    CapabilityRecord,
    CapabilityRequest,
    CapabilityResult,
    PlatformRuntimeReceipt,
    VerticalCoverage,
    VerticalRuntimeReceipt,
)
from apiforge.contracts.risk_complexity import RiskComplexityAssessment
from apiforge.contracts.routing import (
    CandidateAssessment,
    ObservedSignal,
    RoutingDecision,
    RoutingPlan,
    RoutingPolicy,
    RoutingRequest,
    ScorecardFeedback,
)
from apiforge.contracts.routing_evolution import (
    EvidenceCoverage,
    EvolutionPolicy,
    PromotionGate,
    RoutingEvolution,
)
from apiforge.contracts.stubs import (
    AgenticQualityAssessment,
    AnalyticalAccessIR,
    ApiSafetyAssessment,
    CapacityAssessment,
    DataAccessIR,
    DataAccessReadiness,
    DataPerformanceProfile,
    MessagingAccessIR,
    PerformanceRun,
    RuntimeMatrix,
    StreamingAccessIR,
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
from apiforge.contracts.workspace import ProjectManifest, WorkspaceGraph, WorkspaceManifest
from apiforge.core.models import Fact, Finding
from apiforge.evidence.models import Receipt
from apiforge.migration.contracts import (
    DiscoveryResult,
    MigrationFinding,
    MigrationPlan,
    MigrationReadiness,
    MigrationReport,
    MigrationSpec,
    MigrationTask,
    RuntimeCapability,
)

CONTRACTS: dict[str, type[BaseModel]] = {
    "ArtifactRef/v1": ArtifactRef,
    "Fact/v1": Fact,
    "Finding/v1": Finding,
    "Receipt/v1": Receipt,
    "Decision/v1": Decision,
    "ActionPlan/v1": ActionPlan,
    "ActionStep/v1": ActionStep,
    "Verification/v1": Verification,
    "DevinCheck/v1": DevinCheck,
    "DevinCliProbe/v1": DevinCliProbe,
    "DevinLaunch/v1": DevinLaunch,
    "DevinPayload/v1": DevinPayload,
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
    "CapacityAssessment/v1": CapacityAssessment,
    "DataAccessIR/v1": DataAccessIR,
    "DataAccessReadiness/v1": DataAccessReadiness,
    "DataPerformanceProfile/v1": DataPerformanceProfile,
    "MessagingAccessIR/v1": MessagingAccessIR,
    "StreamingAccessIR/v1": StreamingAccessIR,
    "ApiSafetyAssessment/v1": ApiSafetyAssessment,
    "AgenticQualityAssessment/v1": AgenticQualityAssessment,
    "AnalyticalAccessIR/v1": AnalyticalAccessIR,
    "RuntimeMatrix/v1": RuntimeMatrix,
    "WorkloadProfile/v1": WorkloadProfile,
    "TestRecord/v1": TestRecord,
    "VerificationRecord/v1": VerificationRecord,
    "VerificationCheck/v1": VerificationCheck,
    "HoldoutRecord/v1": HoldoutRecord,
    "AgenticRun/v1": AgenticRun,
    "RuntimeReview/v1": RuntimeReview,
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
    "CapabilityRecord/v1": CapabilityRecord,
    "CapabilityRequest/v1": CapabilityRequest,
    "CapabilityResult/v1": CapabilityResult,
    "VerticalCoverage/v1": VerticalCoverage,
    "VerticalRuntimeReceipt/v1": VerticalRuntimeReceipt,
    "ObservedSignal/v1": ObservedSignal,
    "RoutingPolicy/v1": RoutingPolicy,
    "RoutingRequest/v1": RoutingRequest,
    "CandidateAssessment/v1": CandidateAssessment,
    "RoutingDecision/v1": RoutingDecision,
    "RoutingPlan/v1": RoutingPlan,
    "RiskComplexityAssessment/v1": RiskComplexityAssessment,
    "ExpertisePack/v1": ExpertisePack,
    "ScorecardFeedback/v1": ScorecardFeedback,
    "EvidenceRef/v1": EvidenceRef,
    "EvidenceCoverage/v1": EvidenceCoverage,
    "EvolutionPolicy/v1": EvolutionPolicy,
    "PromotionGate/v1": PromotionGate,
    "RoutingEvolution/v1": RoutingEvolution,
    "PlatformRuntimeReceipt/v1": PlatformRuntimeReceipt,
    "ExternalReadRequest/v1": ExternalReadRequest,
    "ExternalReadReceipt/v1": ExternalReadReceipt,
    "ExternalReadResult/v1": ExternalReadResult,
    "GitHubPrReceipt/v1": GitHubPrReceipt,
    "VendorIntent/v1": VendorIntent,
    "IntentDiff/v1": IntentDiff,
    "OperationReceipt/v1": OperationReceipt,
    "ObservabilityFinding/v1": ObservabilityFinding,
    "ReadSafetyPolicy/v1": ReadSafetyPolicy,
    "ReadRetryPolicy/v1": ReadRetryPolicy,
    "CircuitBreakerPolicy/v1": CircuitBreakerPolicy,
    "CircuitBreakerEvent/v1": CircuitBreakerEvent,
    "CircuitBreakerMetrics/v1": CircuitBreakerMetrics,
    "CircuitMetricsExportReceipt/v1": CircuitMetricsExportReceipt,
    "HostExportBinding/v1": HostExportBinding,
    "ObservabilityExportReadiness/v1": ObservabilityExportReadiness,
    "GrpcIR/v1": GrpcIR,
    "GrpcMessage/v1": GrpcMessage,
    "GrpcRpc/v1": GrpcRpc,
    "GrpcService/v1": GrpcService,
    "GrpcDiagnostic/v1": GrpcDiagnostic,
    "GrpcCompatibilityReport/v1": GrpcCompatibilityReport,
    "GrpcCapability/v1": GrpcCapability,
    "GrpcCodegenRequest/v1": GrpcCodegenRequest,
    "GrpcCodegenResult/v1": GrpcCodegenResult,
    "GrpcArtifact/v1": GrpcArtifact,
    "GrpcGatewayRequest/v1": GrpcGatewayRequest,
    "GrpcGatewayProjection/v1": GrpcGatewayProjection,
    "GrpcRuntimePolicy/v1": GrpcRuntimePolicy,
    "GrpcPerformanceRun/v1": GrpcPerformanceRun,
    "GrpcPerformanceReport/v1": GrpcPerformanceReport,
    "GrpcSecurityReport/v1": GrpcSecurityReport,
    "GrpcPlan/v1": GrpcPlan,
    "GrpcVerification/v1": GrpcVerification,
    "MigrationSpec/v1": MigrationSpec,
    "RuntimeCapability/v1": RuntimeCapability,
    "MigrationFinding/v1": MigrationFinding,
    "DiscoveryResult/v1": DiscoveryResult,
    "MigrationReadiness/v1": MigrationReadiness,
    "MigrationTask/v1": MigrationTask,
    "MigrationPlan/v1": MigrationPlan,
    "MigrationReport/v1": MigrationReport,
    "Distribution/v1": DistributionDoctor,
    "ProjectManifest/v1": ProjectManifest,
    "WorkspaceManifest/v1": WorkspaceManifest,
    "ArchitectureGraph/v1": WorkspaceGraph,
    "ContextScope/v1": ContextScope,
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
