"""§53–§57 contracts: run inspection, run comparison and the waste detector."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue

# §57 — every quantitative claim in an inspection carries its evidence basis;
# waste findings additionally admit "hypothesis" (plausible, unproven).
InspectionState = Literal["observed", "partial", "estimated", "unresolved"]

# §56 — the closed waste taxonomy.
WasteKind = Literal[
    "duplicate_context",
    "duplicate_retrieval",
    "repeated_tool_call",
    "repeated_rule_lookup",
    "redundant_agent",
    "redundant_review",
    "unnecessary_debate",
    "oversized_tool_output",
    "full_file_read",
    "premium_model_misuse",
    "repeated_summary",
    "unused_context_expansion",
]


class InspectionMetric(VersionedContract):
    """One named metric inside an inspection section."""

    name: str = Field(min_length=1)
    value: JsonValue | None = None
    state: InspectionState = "observed"
    detail: str = ""

    @model_validator(mode="after")
    def value_matches_state(self) -> InspectionMetric:
        if self.state == "unresolved" and self.value is not None:
            raise ValueError("unresolved metrics carry no value")
        if self.state == "unresolved" and not self.detail:
            raise ValueError("unresolved metrics must name the missing basis")
        if self.state != "unresolved" and self.value is None:
            raise ValueError("observed/partial/estimated metrics require a value")
        return self


class InspectionSection(VersionedContract):
    """One §54 report section (context, memory, tools, models, …)."""

    name: str = Field(min_length=1)
    metrics: tuple[InspectionMetric, ...] = ()


class WasteFinding(VersionedContract):
    """One §56 detector hit, labeled by evidence basis (§57)."""

    schema: Literal["apiforge/waste-finding/v1"] = "apiforge/waste-finding/v1"  # type: ignore[assignment]
    kind: WasteKind
    evidence: Literal["observed", "estimated", "hypothesis"]
    detail: str = ""
    refs: tuple[str, ...] = ()
    estimated_tokens: int | None = Field(default=None, ge=0)


class AgentOpsTimelineEvent(VersionedContract):
    """One ordered event from a run ledger, span ledger or token ledger."""

    event_id: str = Field(min_length=1)
    source: Literal["ledger", "span", "token"]
    operation: str = Field(min_length=1)
    timestamp: str | None = None
    status: str = "observed"
    detail: str = ""


class AgentOpsTimeline(VersionedContract):
    """Deterministic cross-ledger timeline with explicit ordering gaps."""

    schema: Literal["apiforge/agentops-timeline/v1"] = "apiforge/agentops-timeline/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    events: tuple[AgentOpsTimelineEvent, ...] = ()
    unresolved: tuple[str, ...] = ()


class RunInspection(VersionedContract):
    """§53–§54 the full single-run report, also the JSON projection."""

    schema: Literal["apiforge/run-inspection/v1"] = "apiforge/run-inspection/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    task_id: str | None = None
    profile: str | None = None
    risk: str | None = None
    sections: tuple[InspectionSection, ...] = ()
    waste: tuple[WasteFinding, ...] = ()
    decision_path: tuple[str, ...] = ()
    timeline: tuple[AgentOpsTimelineEvent, ...] = ()
    unresolved: tuple[str, ...] = ()


class ComparisonAxis(VersionedContract):
    """One §55 axis: a/b values, delta and a deterministic verdict."""

    axis: str = Field(min_length=1)
    a: JsonValue | None = None
    b: JsonValue | None = None
    delta: float | None = None
    verdict: Literal["a", "b", "tie", "unresolved"]
    detail: str = ""


class RunComparison(VersionedContract):
    """§55 the two-run comparison over the declared axis set."""

    schema: Literal["apiforge/run-comparison/v1"] = "apiforge/run-comparison/v1"  # type: ignore[assignment]
    run_a: str = Field(min_length=1)
    run_b: str = Field(min_length=1)
    axes: tuple[ComparisonAxis, ...] = ()
    unresolved: tuple[str, ...] = ()


class WasteReport(VersionedContract):
    """§56–§57 detector output for one run."""

    schema: Literal["apiforge/waste-report/v1"] = "apiforge/waste-report/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    findings: tuple[WasteFinding, ...] = ()
    unresolved: tuple[str, ...] = ()


__all__ = [
    "AgentOpsTimeline",
    "AgentOpsTimelineEvent",
    "ComparisonAxis",
    "InspectionMetric",
    "InspectionSection",
    "InspectionState",
    "RunComparison",
    "RunInspection",
    "WasteFinding",
    "WasteKind",
    "WasteReport",
]
