"""Knowledge source and freshness contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceRecord

FreshnessState = Literal["fresh", "stale", "unresolved", "unknown"]


class PackFreshness(VersionedContract):
    """Optional metadata declared by a Knowledge Pack."""

    window_days: int | None = Field(default=None, ge=0)
    source_hash: str | None = None
    authority: str | None = None


class SourceObservation(VersionedContract):
    """Read-only observation receipt; it does not update a pack."""

    source: str
    observed_at: str
    source_hash: str | None = None
    source_version: str | None = None
    receipt_ref: str
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)


class FreshnessResult(VersionedContract):
    state: FreshnessState
    source: str
    observed_at: str | None = None
    age_days: int | None = Field(default=None, ge=0)
    reason: str
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    next_action: str = "review"
