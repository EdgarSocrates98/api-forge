"""Canonical versioned contracts (``<Name>/v1``) and their registry."""

from apiforge.contracts.adapter import (
    AdapterCapability,
    AdapterExecution,
    AdapterMode,
    AdapterStatus,
    EvidenceLevel,
)
from apiforge.contracts.data_runtime import DataProvider, DataReadReceipt, DataReadRequest
from apiforge.contracts.integration import (
    ExternalReadReceipt,
    ExternalReadRequest,
    ExternalReadResult,
    GitHubPrReceipt,
)
from apiforge.contracts.platform import (
    CapabilityRecord,
    CapabilityRequest,
    CapabilityResult,
    PlatformRuntimeReceipt,
    VerticalCoverage,
    VerticalRuntimeReceipt,
)
from apiforge.contracts.sandbox import SandboxCommand, SandboxCommandResult

__all__ = [
    "AdapterCapability",
    "AdapterExecution",
    "AdapterMode",
    "AdapterStatus",
    "CapabilityRecord",
    "CapabilityRequest",
    "CapabilityResult",
    "DataProvider",
    "DataReadReceipt",
    "DataReadRequest",
    "EvidenceLevel",
    "ExternalReadReceipt",
    "ExternalReadRequest",
    "ExternalReadResult",
    "GitHubPrReceipt",
    "PlatformRuntimeReceipt",
    "SandboxCommand",
    "SandboxCommandResult",
    "VerticalCoverage",
    "VerticalRuntimeReceipt",
]
