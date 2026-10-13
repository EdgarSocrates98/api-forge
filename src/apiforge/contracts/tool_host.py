"""Tool/host economy contracts: test and error slices, tool surface cost, host projections."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

OutputMode = Literal["json", "compact"]
SurfaceName = Literal["full", "compact"]


class TestFailure(VersionedContract):
    """One failing (or erroring) test — always emitted, never budget-trimmed."""

    __test__ = False  # not a pytest class

    test: str = Field(min_length=1)
    outcome: Literal["failed", "error"] = "failed"
    file: str | None = None
    line: int | None = Field(default=None, ge=1)
    assertion: str = ""
    signature: str = ""
    span: tuple[int, int] | None = None


class TestSlice(VersionedContract):
    """What a test run said, without the thousands of lines it took to say it (§43)."""

    __test__ = False

    schema: Literal["apiforge/test-slice/v1"] = "apiforge/test-slice/v1"  # type: ignore[assignment]
    format: Literal["pytest", "junit"]
    passed: int = Field(default=0, ge=0)
    failed: int = Field(default=0, ge=0)
    errors: int = Field(default=0, ge=0)
    skipped: int = Field(default=0, ge=0)
    failures: tuple[TestFailure, ...] = ()
    log_ref: str
    original_bytes: int = Field(ge=0)
    slice_bytes: int = Field(default=0, ge=0)
    unresolved: tuple[str, ...] = ()


class ErrorSignature(VersionedContract):
    """A normalized failure signature with its evidence spans (§44)."""

    signature: str = Field(min_length=1)
    first_line: str = Field(min_length=1)
    count: int = Field(ge=1)
    spans: tuple[tuple[int, int], ...] = ()
    frames: tuple[str, ...] = ()
    context: tuple[str, ...] = ()


class ErrorSlice(VersionedContract):
    schema: Literal["apiforge/error-slice/v1"] = "apiforge/error-slice/v1"  # type: ignore[assignment]
    signatures: tuple[ErrorSignature, ...] = ()
    environment: tuple[str, ...] = ()
    log_ref: str
    original_bytes: int = Field(ge=0)
    original_lines: int = Field(ge=0)
    slice_bytes: int = Field(default=0, ge=0)


class ToolCost(VersionedContract):
    name: str = Field(min_length=1)
    name_bytes: int = Field(ge=0)
    description_bytes: int = Field(ge=0)
    schema_bytes: int = Field(ge=0)


class ToolSurface(VersionedContract):
    """Measured cost of an MCP surface (§91): names, descriptions and schemas."""

    schema: Literal["apiforge/tool-surface/v1"] = "apiforge/tool-surface/v1"  # type: ignore[assignment]
    surface: SurfaceName
    tools: tuple[ToolCost, ...] = ()
    tool_count: int = Field(ge=0)
    total_bytes: int = Field(ge=0)
    reachable_capabilities: int = Field(ge=0)
    schema_source: Literal["signature"] = "signature"


class HostProjection(VersionedContract):
    """Declared host projection (§92–93); the core never branches on host."""

    schema: Literal["apiforge/host-projection/v1"] = "apiforge/host-projection/v1"  # type: ignore[assignment]
    host: str = Field(min_length=1)
    instruction_file: str = ""
    mcp_surface: SurfaceName
    output: OutputMode
    deferred_tools: bool = False
    surface_bytes: int = Field(default=0, ge=0)
    full_surface_bytes: int = Field(default=0, ge=0)
    verb_map: dict[str, str] = Field(default_factory=dict)
    notes: tuple[str, ...] = ()


__all__ = [
    "ErrorSignature",
    "ErrorSlice",
    "HostProjection",
    "OutputMode",
    "SurfaceName",
    "TestFailure",
    "TestSlice",
    "ToolCost",
    "ToolSurface",
]
