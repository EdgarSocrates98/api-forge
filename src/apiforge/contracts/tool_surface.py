"""Versioned contracts for tool-surface engineering v2 (§40–§43)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue

# §40 — the closed audit finding taxonomy.
SurfaceFindingKind = Literal[
    "redundant",
    "overlapping",
    "oversized_schema",
    "oversized_output",
    "poor_description",
    "unbounded_list",
]

EvidenceBasis = Literal["observed", "estimated", "hypothesis"]


class SurfaceFinding(VersionedContract):
    """One §40 audit hit on the measured surface."""

    schema: Literal["apiforge/surface-finding/v1"] = "apiforge/surface-finding/v1"  # type: ignore[assignment]
    kind: SurfaceFindingKind
    tool: str = Field(min_length=1)
    evidence: EvidenceBasis
    detail: str = ""
    refs: tuple[str, ...] = ()


class ToolSurfaceAudit(VersionedContract):
    """§40 the audited surface: every finding labeled by evidence basis."""

    schema: Literal["apiforge/tool-surface-audit/v1"] = "apiforge/tool-surface-audit/v1"  # type: ignore[assignment]
    surface: Literal["full", "compact"] = "full"
    tool_count: int = Field(ge=0)
    total_bytes: int = Field(ge=0)
    findings: tuple[SurfaceFinding, ...] = ()
    accepted: tuple[SurfaceFinding, ...] = ()
    unresolved: tuple[str, ...] = ()


class ToolDisclosure(VersionedContract):
    """§41 task -> capability router -> active tool set (advisory).

    The host decides what it actually loads; this contract declares which
    tools a task class needs and which it provably does not.
    """

    schema: Literal["apiforge/tool-disclosure/v1"] = "apiforge/tool-disclosure/v1"  # type: ignore[assignment]
    task: str = Field(min_length=1)
    task_class: str = Field(min_length=1)
    active_tools: tuple[str, ...] = ()
    dropped_tools: tuple[str, ...] = ()
    basis: str = "declared-policy"
    unresolved: tuple[str, ...] = ()


class PageWindow(VersionedContract):
    """§42 pagination window over a bounded item list."""

    offset: int = Field(ge=0)
    limit: int = Field(ge=1)
    total: int = Field(ge=0)
    next_offset: int | None = Field(default=None, ge=0)


class ToolPage(VersionedContract):
    """§42 the standardized large-response shape.

    ``summary`` describes the whole set; ``items`` is the bounded window;
    ``refs`` points at full artifacts; ``unresolved`` names what could not
    be represented; ``pagination`` declares the window honestly.
    """

    schema: Literal["apiforge/tool-page/v1"] = "apiforge/tool-page/v1"  # type: ignore[assignment]
    summary: str = ""
    items: tuple[JsonValue, ...] = ()
    refs: tuple[str, ...] = ()
    evidence: tuple[JsonValue, ...] = ()
    unresolved: tuple[str, ...] = ()
    pagination: PageWindow


class ToolBenchmarkSample(VersionedContract):
    """§43 one measured invocation of a read-only tool."""

    tool: str = Field(min_length=1)
    response_bytes: int = Field(ge=0)
    tokens_est: int = Field(ge=0)


class ToolBenchmark(VersionedContract):
    """§43 aggregated cost for one tool over declared samples."""

    schema: Literal["apiforge/tool-benchmark/v1"] = "apiforge/tool-benchmark/v1"  # type: ignore[assignment]
    tool: str = Field(min_length=1)
    samples: int = Field(ge=0)
    median_bytes: int = Field(ge=0)
    p95_bytes: int = Field(ge=0)
    median_tokens_est: int = Field(ge=0)
    p95_tokens_est: int = Field(ge=0)
    usefulness: Literal["met", "missed", "unresolved"] = "unresolved"
    basis: Literal["estimated"] = "estimated"


class ToolBenchmarkReport(VersionedContract):
    """§43 ranking of the most expensive tools on the declared sample set."""

    schema: Literal["apiforge/tool-benchmark-report/v1"] = "apiforge/tool-benchmark-report/v1"  # type: ignore[assignment]
    tools: tuple[ToolBenchmark, ...] = ()
    ranking: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


class DisclosurePolicy(VersionedContract):
    """§41 the declared task-class -> tool set mapping (rules file shape)."""

    schema: Literal["apiforge/disclosure-policy/v1"] = "apiforge/disclosure-policy/v1"  # type: ignore[assignment]
    task_classes: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    keywords: dict[str, tuple[str, ...]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def classes_have_tools(self) -> DisclosurePolicy:
        for name, tools in self.task_classes.items():
            if not tools:
                raise ValueError(f"task class {name!r} declares no tools")
        return self


__all__ = [
    "DisclosurePolicy",
    "EvidenceBasis",
    "PageWindow",
    "SurfaceFinding",
    "SurfaceFindingKind",
    "ToolBenchmark",
    "ToolBenchmarkReport",
    "ToolBenchmarkSample",
    "ToolDisclosure",
    "ToolPage",
    "ToolSurfaceAudit",
]
