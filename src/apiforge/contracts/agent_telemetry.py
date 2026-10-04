"""Closed local OTel-shaped contracts for agent and tool execution spans."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue, Sha256, freeze_json

SpanOperation = Literal[
    "invoke_agent", "execute_tool", "handoff", "decision", "retrieval", "checkpoint"
]
SpanStatus = Literal["unset", "ok", "error", "unresolved"]

_SENSITIVE_ATTRIBUTE_MARKERS = (
    "api_key",
    "authorization",
    "cookie",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "access_token",
)
SENSITIVE_ATTRIBUTE_CODE = "AF-OTEL-SENSITIVE-ATTRIBUTE"


class AgentSpan(VersionedContract):
    """One local evidence span aligned with agent/tool semantic conventions."""

    schema: Literal["apiforge/agent-span/v1"] = "apiforge/agent-span/v1"  # type: ignore[assignment]
    span_id: str = Field(pattern=r"^span:[0-9a-f]{16}$")
    trace_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    parent_span_id: str | None = None
    operation: SpanOperation
    agent_name: str | None = None
    tool_name: str | None = None
    started_at: str = Field(min_length=1)
    ended_at: str | None = None
    status: SpanStatus = "unset"
    status_message: str = ""
    attributes: Mapping[str, JsonValue] = Field(default_factory=dict)
    events: tuple[str, ...] = ()
    links: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    content_sha256: Sha256

    @field_validator("attributes", mode="after")
    @classmethod
    def freeze_safe_attributes(cls, value: object) -> JsonValue:
        if not isinstance(value, Mapping):
            raise TypeError("attributes must be an object")
        for key in value:
            normalized = str(key).lower().replace("-", "_")
            if any(marker in normalized for marker in _SENSITIVE_ATTRIBUTE_MARKERS):
                raise ValueError(f"{SENSITIVE_ATTRIBUTE_CODE}: {key}")
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise TypeError("attributes must be an object")
        return frozen


class AgentSpanQuery(VersionedContract):
    """Bounded local span lookup."""

    schema: Literal["apiforge/agent-span-query/v1"] = "apiforge/agent-span-query/v1"  # type: ignore[assignment]
    task_id: str | None = None
    run_id: str | None = None
    trace_id: str | None = None
    operation: SpanOperation | None = None
    status: SpanStatus | None = None
    max_results: int = Field(default=100, ge=1, le=1000)


class AgentSpanResult(VersionedContract):
    """Bounded span response with corruption/unresolved visibility."""

    schema: Literal["apiforge/agent-span-result/v1"] = "apiforge/agent-span-result/v1"  # type: ignore[assignment]
    query: AgentSpanQuery
    spans: tuple[AgentSpan, ...] = ()
    unresolved: tuple[str, ...] = ()
    status: Literal["ready", "degraded", "unresolved"] = "ready"


__all__ = ["AgentSpan", "AgentSpanQuery", "AgentSpanResult", "SpanOperation", "SpanStatus"]
