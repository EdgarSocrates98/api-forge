"""Canonical versioned contracts (``<Name>/v1``) and their registry."""

from apiforge.contracts.adapter import (
    AdapterCapability,
    AdapterExecution,
    AdapterMode,
    AdapterStatus,
    EvidenceLevel,
)
from apiforge.contracts.compatibility import CompatibilityCell, CompatibilityMatrix, RuntimeReceipt
from apiforge.contracts.data_runtime import DataProvider, DataReadReceipt, DataReadRequest
from apiforge.contracts.debate import (
    AdaptivePlan,
    AdaptivePolicy,
    DebateReplay,
    ParticipantDeclaration,
)
from apiforge.contracts.devin import (
    DevinCheck,
    DevinCliProbe,
    DevinLaunch,
    DevinPayload,
    DevinPermissionMode,
    DevinPromptTransport,
    DevinSurface,
    DevinTaskKind,
)
from apiforge.contracts.evidence import EvidenceKind, EvidenceRecord, EvidenceRef
from apiforge.contracts.experience import ExperienceAction, ExperienceSnapshot, ExperienceView
from apiforge.contracts.host import (
    HostCapability,
    HostCapabilityRequest,
    HostDeclaration,
    HostResolution,
)
from apiforge.contracts.integration import (
    ExternalReadReceipt,
    ExternalReadRequest,
    ExternalReadResult,
    GitHubPrReceipt,
)
from apiforge.contracts.knowledge import (
    FreshnessResult,
    KnowledgeObservation,
    PackFreshness,
    SourceObservation,
)
from apiforge.contracts.platform import (
    CapabilityRecord,
    CapabilityRequest,
    CapabilityResult,
    PlatformRuntimeReceipt,
    VerticalCoverage,
    VerticalRuntimeReceipt,
)
from apiforge.contracts.routing import (
    CandidateAssessment,
    ObservedSignal,
    RoutingDecision,
    RoutingPolicy,
    RoutingRequest,
    ScorecardFeedback,
)
from apiforge.contracts.routing_evolution import (
    EvidenceCoverage,
    EvolutionMode,
    EvolutionPolicy,
    PromotionGate,
    PromotionState,
    RoutingEvolution,
)
from apiforge.contracts.sandbox import SandboxCommand, SandboxCommandResult

__all__ = [
    "AdapterCapability",
    "AdapterExecution",
    "AdapterMode",
    "AdapterStatus",
    "AdaptivePlan",
    "AdaptivePolicy",
    "CandidateAssessment",
    "CapabilityRecord",
    "CapabilityRequest",
    "CapabilityResult",
    "CompatibilityCell",
    "CompatibilityMatrix",
    "DataProvider",
    "DataReadReceipt",
    "DataReadRequest",
    "DebateReplay",
    "DevinCheck",
    "DevinCliProbe",
    "DevinLaunch",
    "DevinPayload",
    "DevinPermissionMode",
    "DevinPromptTransport",
    "DevinSurface",
    "DevinTaskKind",
    "EvidenceCoverage",
    "EvidenceKind",
    "EvidenceLevel",
    "EvidenceRecord",
    "EvidenceRef",
    "EvolutionMode",
    "EvolutionPolicy",
    "ExperienceAction",
    "ExperienceSnapshot",
    "ExperienceView",
    "ExternalReadReceipt",
    "ExternalReadRequest",
    "ExternalReadResult",
    "FreshnessResult",
    "GitHubPrReceipt",
    "HostCapability",
    "HostCapabilityRequest",
    "HostDeclaration",
    "HostResolution",
    "KnowledgeObservation",
    "ObservedSignal",
    "PackFreshness",
    "ParticipantDeclaration",
    "PlatformRuntimeReceipt",
    "PromotionGate",
    "PromotionState",
    "RoutingDecision",
    "RoutingEvolution",
    "RoutingPolicy",
    "RoutingRequest",
    "RuntimeReceipt",
    "SandboxCommand",
    "SandboxCommandResult",
    "ScorecardFeedback",
    "SourceObservation",
    "VerticalCoverage",
    "VerticalRuntimeReceipt",
]
