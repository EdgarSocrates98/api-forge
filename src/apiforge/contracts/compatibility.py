"""Observed runtime compatibility matrix contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceLevel, EvidenceRecord

CellState = Literal["passed", "failed", "unresolved"]


class RuntimeReceipt(VersionedContract):
    ecosystem: str
    runtime_version: str
    environment: str
    state: CellState
    observed_at: str
    command: str
    receipt_ref: str
    output_hash: str | None = None
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    evidence_level: EvidenceLevel = "observed"


class CompatibilityCell(VersionedContract):
    ecosystem: str
    runtime_version: str
    state: CellState = "unresolved"
    receipts: tuple[RuntimeReceipt, ...] = ()
    limitations: tuple[str, ...] = ()
    evidence_level: EvidenceLevel = "unknown"


class CompatibilityMatrix(VersionedContract):
    ecosystem: str
    cells: tuple[CompatibilityCell, ...] = ()
    observed_versions: tuple[str, ...] = ()
    unresolved_versions: tuple[str, ...] = ()
    evidence_level: EvidenceLevel = "unknown"
