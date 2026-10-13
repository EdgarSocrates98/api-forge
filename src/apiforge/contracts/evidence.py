"""Shared evidence contracts used by every interoperability surface.

Evidence is intentionally descriptive rather than a score.  A declaration or
heuristic can never silently become a verification claim without a receipt.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract

EvidenceLevel = Literal["observed", "declared", "inferred", "heuristic", "verified", "unknown"]
EvidenceKind = Literal[
    "trace",
    "receipt",
    "evaluation",
    "fixture",
    "policy",
    "rollback",
    "knowledge",
]

__all__ = ["EvidenceKind", "EvidenceLevel", "EvidenceRecord", "EvidenceRef", "can_promote"]


class EvidenceRef(VersionedContract):
    """Typed reference to evidence without claiming its semantic validity."""

    ref: str
    kind: EvidenceKind = "trace"
    level: EvidenceLevel = "unknown"
    limitations: tuple[str, ...] = ()

    @field_validator("limitations", mode="after")
    @classmethod
    def normalize_limitations(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))


class EvidenceRecord(VersionedContract):
    """Provenance for a claim, artifact or projection."""

    level: EvidenceLevel = "unknown"
    source: str = "unknown"
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @field_validator("refs", "limitations", mode="after")
    @classmethod
    def normalize_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))


def can_promote(level: EvidenceLevel, target: EvidenceLevel) -> bool:
    """Return whether a target is no stronger than the current evidence.

    ``unknown`` is deliberately weakest and ``verified`` strongest.  The
    semantic ordering is only used for conservative promotion checks; it is
    not a replacement for the receipt itself.
    """

    order = {
        "unknown": 0,
        "heuristic": 1,
        "inferred": 2,
        "declared": 3,
        "observed": 4,
        "verified": 5,
    }
    return order[level] >= order[target]
