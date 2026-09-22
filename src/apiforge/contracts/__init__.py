"""Canonical versioned contracts (``<Name>/v1``) and their registry."""

from apiforge.contracts.adapter import (
    AdapterCapability,
    AdapterExecution,
    AdapterMode,
    AdapterStatus,
    EvidenceLevel,
)
from apiforge.contracts.data_runtime import DataProvider, DataReadReceipt, DataReadRequest
from apiforge.contracts.platform import (
    CapabilityRecord,
    CapabilityRequest,
    CapabilityResult,
    VerticalCoverage,
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
    "SandboxCommand",
    "SandboxCommandResult",
    "VerticalCoverage",
]
