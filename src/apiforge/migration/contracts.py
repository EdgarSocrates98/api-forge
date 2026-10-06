"""Versioned contracts for runtime migration analysis."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.task import OutcomeBrief, TaskSpec

Ecosystem = Literal["java", "python", "go"]
Severity = Literal["info", "low", "medium", "high", "critical"]


class MigrationSpec(VersionedContract):
    """Closed, read-only input for a runtime migration."""

    project_root: str
    ecosystem: Ecosystem
    source_version: str
    target_version: str
    framework: str | None = None
    build_tool: str | None = None
    package_manager: str | None = None
    contract_paths: tuple[str, ...] = ()
    integration_kinds: tuple[str, ...] = ()
    read_only: bool = True
    max_parallel_agents: int = Field(default=4, ge=1, le=64)

    @model_validator(mode="after")
    def validate_versions(self) -> MigrationSpec:
        if not self.source_version.strip() or not self.target_version.strip():
            raise ValueError("source_version and target_version are required")
        if not self.read_only:
            raise ValueError("runtime migration MVP is read-only")
        return self

    def identity(self) -> str:
        return f"{self.ecosystem}:{self.source_version}->{self.target_version}:{self.project_root}"


class RuntimeCapability(VersionedContract):
    name: str
    available: bool
    evidence: tuple[str, ...] = ()
    limitation: str | None = None


class MigrationReadiness(VersionedContract):
    status: Literal["ready", "review", "blocked"]
    direction: Literal["upgrade", "downgrade", "same"]
    intermediate_versions: tuple[str, ...] = ()
    missing_capabilities: tuple[str, ...] = ()
    blocking_findings: tuple[str, ...] = ()


class MigrationFinding(VersionedContract):
    rule_id: str
    severity: Severity
    message: str
    source: str
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    blocking: bool = False


class DiscoveryResult(VersionedContract):
    spec_identity: str
    ecosystem: Ecosystem
    detected_files: tuple[str, ...] = ()
    capabilities: tuple[RuntimeCapability, ...] = ()
    findings: tuple[MigrationFinding, ...] = ()
    input_hashes: tuple[tuple[str, str], ...] = ()


class MigrationTask(VersionedContract):
    id: str
    axis: str
    outcome: str
    dependencies: tuple[str, ...] = ()
    writable_paths: tuple[str, ...] = ()
    evidence_required: tuple[str, ...] = ()
    risk: Literal["read_only", "local_reversible"] = "read_only"


class MigrationPlan(VersionedContract):
    spec_identity: str
    task: TaskSpec
    tasks: tuple[MigrationTask, ...] = ()
    findings: tuple[MigrationFinding, ...] = ()
    capabilities: tuple[RuntimeCapability, ...] = ()
    readiness: MigrationReadiness | None = None


class MigrationReport(VersionedContract):
    spec_identity: str
    discovery: DiscoveryResult
    plan: MigrationPlan
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    outcome: OutcomeBrief | None = None
