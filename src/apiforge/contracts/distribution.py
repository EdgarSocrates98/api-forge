"""Contracts for installed API Forge paths, assets and local diagnostics."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceLevel, EvidenceRecord

CapabilityState = Literal["ready", "unavailable", "degraded", "unresolved", "blocked"]
PathSource = Literal["default", "environment", "config", "manifest", "cli"]


class ForgePaths(VersionedContract):
    """Resolved package and user-owned paths used by a local invocation."""

    schema: Literal["apiforge/distribution/v1"] = "apiforge/distribution/v1"  # type: ignore[assignment]
    package_root: str
    executable: str
    state_root: str
    config_path: str | None = None
    cache_root: str
    project_root: str | None = None
    workspace_root: str | None = None
    sources: tuple[tuple[str, PathSource], ...] = ()


class AssetStatus(VersionedContract):
    """Correspondence status for one package-owned asset."""

    asset: str
    path: str
    sha256: str | None = None
    state: Literal["present", "missing", "diverged", "unresolved"] = "present"
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    limitations: tuple[str, ...] = ()


class CapabilityDiagnostic(VersionedContract):
    """One doctor capability result with an actionable unlock."""

    capability: str
    state: CapabilityState
    detail: str = ""
    field: str = "capability"
    unlock: str = "inspect the detail and rerun doctor"
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)


class DistributionDoctor(VersionedContract):
    """Canonical offline installation and capability diagnostic."""

    schema: Literal["apiforge/doctor/v1"] = "apiforge/doctor/v1"  # type: ignore[assignment]
    status: Literal["ready", "degraded", "unresolved", "blocked"] = "ready"
    paths: ForgePaths
    capabilities: tuple[CapabilityDiagnostic, ...] = ()
    assets: tuple[AssetStatus, ...] = ()
    gaps: tuple[str, ...] = ()
    evidence_level: EvidenceLevel = "observed"


class DistributionRefusal(VersionedContract):
    """Serializable refusal shape shared by CLI and MCP boundaries."""

    code: str
    field: str
    detail: str
    unlock: str
    evidence: tuple[str, ...] = ()
