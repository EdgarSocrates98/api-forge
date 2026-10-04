"""Provider-free append-only storage for local agent/tool execution spans."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from apiforge.contracts.agent_telemetry import AgentSpan, AgentSpanQuery, AgentSpanResult
from apiforge.core.io import sha256_file
from apiforge.core.models import JsonValue

_DIR = Path(".apiforge") / "telemetry"
_FILE = "agent-spans.jsonl"
STORE_CORRUPT_CODE = "AF-OTEL-STORE-CORRUPT"
SPAN_CONFLICT_CODE = "AF-OTEL-SPAN-CONFLICT"


def _directory(root: Path) -> Path:
    resolved = Path(root).resolve()
    if resolved.name == ".apiforge":
        resolved = resolved.parent
    return resolved / _DIR


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _append(directory: Path, span: AgentSpan) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / _FILE
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(span.model_dump_json(exclude_none=True, by_alias=True))
        handle.write("\n")
    return path


def _read(directory: Path) -> list[AgentSpan]:
    path = directory / _FILE
    if not path.is_file():
        return []
    spans: list[AgentSpan] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            spans.append(AgentSpan.model_validate(json.loads(line)))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"{STORE_CORRUPT_CODE}: {path}:{line_no}: {exc}") from exc
    return spans


def build_span(
    *,
    trace_id: str,
    task_id: str,
    run_id: str,
    operation: str,
    started_at: str,
    parent_span_id: str | None = None,
    agent_id: str | None = None,
    model_call_id: str | None = None,
    tool_call_id: str | None = None,
    decision_id: str | None = None,
    memory_id: str | None = None,
    context_id: str | None = None,
    agent_name: str | None = None,
    tool_name: str | None = None,
    ended_at: str | None = None,
    status: str = "unset",
    status_message: str = "",
    attributes: dict[str, object] | None = None,
    events: tuple[str, ...] = (),
    links: tuple[str, ...] = (),
    evidence_refs: tuple[str, ...] = (),
    unresolved: tuple[str, ...] = (),
) -> AgentSpan:
    body: dict[str, object] = {
        "trace_id": trace_id,
        "task_id": task_id,
        "run_id": run_id,
        "parent_span_id": parent_span_id,
        "agent_id": agent_id,
        "model_call_id": model_call_id,
        "tool_call_id": tool_call_id,
        "decision_id": decision_id,
        "memory_id": memory_id,
        "context_id": context_id,
        "operation": operation,
        "agent_name": agent_name,
        "tool_name": tool_name,
        "started_at": started_at,
        "ended_at": ended_at,
        "status": status,
        "status_message": status_message,
        "attributes": attributes or {},
        "events": events,
        "links": links,
        "evidence_refs": evidence_refs,
        "unresolved": unresolved,
    }
    digest = _digest(body)
    return AgentSpan(
        span_id=f"span:{digest[:16]}",
        trace_id=trace_id,
        task_id=task_id,
        run_id=run_id,
        parent_span_id=parent_span_id,
        agent_id=agent_id,
        model_call_id=model_call_id,
        tool_call_id=tool_call_id,
        decision_id=decision_id,
        memory_id=memory_id,
        context_id=context_id,
        operation=cast(Any, operation),
        agent_name=agent_name,
        tool_name=tool_name,
        started_at=started_at,
        ended_at=ended_at,
        status=cast(Any, status),
        status_message=status_message,
        attributes=cast(dict[str, JsonValue], attributes or {}),
        events=events,
        links=links,
        evidence_refs=evidence_refs,
        unresolved=unresolved,
        content_sha256=digest,
    )


def append_span(root: Path, span: AgentSpan) -> dict[str, object]:
    """Append one span idempotently; conflicting identity is refused."""
    existing = _read(_directory(root))
    for item in existing:
        if item.span_id == span.span_id:
            if item.content_sha256 != span.content_sha256:
                raise ValueError(f"{SPAN_CONFLICT_CODE}: span_id maps to a different content hash")
            return {"status": "deduplicated", "span": item.model_dump(mode="json")}
    _append(_directory(root), span)
    return {"status": "accepted", "span": span.model_dump(mode="json")}


def query_spans(root: Path, query: AgentSpanQuery) -> AgentSpanResult:
    matches = []
    for span in _read(_directory(root)):
        if query.task_id is not None and span.task_id != query.task_id:
            continue
        if query.run_id is not None and span.run_id != query.run_id:
            continue
        if query.trace_id is not None and span.trace_id != query.trace_id:
            continue
        if query.operation is not None and span.operation != query.operation:
            continue
        if query.status is not None and span.status != query.status:
            continue
        matches.append(span)
    return AgentSpanResult(query=query, spans=tuple(matches[: query.max_results]))


def telemetry_digest(root: Path) -> str | None:
    path = _directory(root) / _FILE
    return sha256_file(path) if path.is_file() else None


__all__ = ["append_span", "build_span", "query_spans", "telemetry_digest"]
