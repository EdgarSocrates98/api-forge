"""Cross-plane agentic health contracts (`doctor --agentic`)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.economy_extras import DoctorFinding

PlaneState = Literal["ok", "attention", "unresolved"]


class AgenticDoctorSection(VersionedContract):
    """Health for one plane; state is never invented — missing inputs
    resolve to ``unresolved`` with the reason named."""

    plane: str = Field(min_length=1)
    state: PlaneState = "ok"
    checks: tuple[str, ...] = ()
    findings: tuple[DoctorFinding, ...] = ()
    unresolved: tuple[str, ...] = ()


class AgenticDoctorReport(VersionedContract):
    """Aggregate agentic health across the declared planes.

    Read-only and local-first: every section reads persisted state only;
    nothing calls a provider, a host or the network.
    """

    schema: Literal["apiforge/agentic-doctor/v1"] = "apiforge/agentic-doctor/v1"  # type: ignore[assignment]
    sections: tuple[AgenticDoctorSection, ...] = ()
    findings: tuple[DoctorFinding, ...] = ()
    unresolved: tuple[str, ...] = ()
    status: Literal["ok", "attention", "unresolved"] = "ok"
