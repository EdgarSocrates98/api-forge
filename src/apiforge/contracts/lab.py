"""API Forge Lab scenario catalog contracts (§28).

The lab is opt-in, isolated, local-first and evidence-producing: every
scenario cell either points at a real fixture/eval or names its declared
gap. Empty pointers are honest gaps, never fabricated coverage.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

LabScenarioState = Literal["covered", "declared-gap"]


class LabScenario(VersionedContract):
    """One §28 scenario cell and its declared coverage state."""

    kind: str = Field(min_length=1)
    state: LabScenarioState
    fixture: str | None = None
    eval_id: str | None = None
    proof: str | None = None
    note: str | None = None
    gap: str | None = None


class LabReport(VersionedContract):
    """Catalog of declared lab scenarios with coverage totals."""

    schema: Literal["apiforge/lab-scenarios/v1"] = "apiforge/lab-scenarios/v1"  # type: ignore[assignment]
    scenarios: tuple[LabScenario, ...] = ()
    totals: dict[str, int] = Field(default_factory=dict)
    unresolved: tuple[str, ...] = ()
