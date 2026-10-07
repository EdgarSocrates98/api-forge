"""Deterministic OTLP/JSON export for local agent spans plus §52 collector acceptance.

No OpenTelemetry SDK dependency: the exporter emits the canonical
``ExportTraceServiceRequest`` JSON shape directly and the validator checks
the exact structure a collector requires. The probe POSTs that payload to a
real collector's OTLP/HTTP endpoint and counts accepted spans in the
collector's declared output file — acceptance is never claimed without it.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from apiforge.contracts.agent_telemetry import AgentSpan, CorrelationIds
from apiforge.contracts.base import ContractError
from apiforge.contracts.otel_export import CollectorProbe, OtlpExport, OtlpValidation
from apiforge.core.io import sha256_file
from apiforge.runtime.agent_telemetry import _directory, _read

TRACEPARENT_INVALID_CODE = "AF-OTEL-TRACEPARENT-INVALID"
EXPORT_INVALID_CODE = "AF-OTEL-EXPORT-INVALID"
COLLECTOR_REFUSED_CODE = "AF-OTEL-COLLECTOR-REFUSED"
COLLECTOR_TIMEOUT_CODE = "AF-OTEL-COLLECTOR-TIMEOUT"
COLLECTOR_UNRESOLVED_CODE = "AF-OTEL-COLLECTOR-UNRESOLVED"

_SCOPE_NAME = "apiforge.telemetry"
_SCOPE_VERSION = "1"
_HEX32 = frozenset("0123456789abcdef")
_CLIENT_OPERATIONS = frozenset({"invoke_model", "execute_tool", "retrieval"})


def new_trace_id() -> str:
    """Fresh W3C trace id: 32 lowercase hex chars."""
    return secrets.token_hex(16)


def new_span_id() -> str:
    """Fresh W3C span id: 16 lowercase hex chars."""
    return secrets.token_hex(8)


def traceparent(trace_id: str, span_id: str, *, sampled: bool = True) -> str:
    """Serialize a W3C ``traceparent`` header value (version 00)."""
    if len(trace_id) != 32 or not set(trace_id) <= _HEX32:
        raise ContractError(
            TRACEPARENT_INVALID_CODE, f"trace_id must be 32 hex chars: {trace_id!r}"
        )
    if len(span_id) != 16 or not set(span_id) <= _HEX32:
        raise ContractError(TRACEPARENT_INVALID_CODE, f"span_id must be 16 hex chars: {span_id!r}")
    return f"00-{trace_id}-{span_id}-{'01' if sampled else '00'}"


def parse_traceparent(value: str) -> tuple[str, str, bool]:
    """Parse ``00-<32hex>-<16hex>-<flags>`` → (trace_id, span_id, sampled)."""
    parts = value.strip().split("-")
    if len(parts) != 4 or parts[0] != "00":
        raise ContractError(TRACEPARENT_INVALID_CODE, f"not a v00 traceparent: {value!r}")
    trace_id, span_id, flags = parts[1].lower(), parts[2].lower(), parts[3]
    if len(trace_id) != 32 or not set(trace_id) <= _HEX32:
        raise ContractError(TRACEPARENT_INVALID_CODE, f"bad trace id in {value!r}")
    if len(span_id) != 16 or not set(span_id) <= _HEX32:
        raise ContractError(TRACEPARENT_INVALID_CODE, f"bad span id in {value!r}")
    if len(flags) != 2 or not set(flags) <= _HEX32:
        raise ContractError(TRACEPARENT_INVALID_CODE, f"bad flags in {value!r}")
    return trace_id, span_id, bool(int(flags, 16) & 1)


def correlation_ids(
    *,
    task_id: str | None = None,
    run_id: str | None = None,
    trace_id: str | None = None,
    span_id: str | None = None,
    agent_id: str | None = None,
    model_call_id: str | None = None,
    tool_call_id: str | None = None,
    decision_id: str | None = None,
    memory_id: str | None = None,
    context_id: str | None = None,
    issue_trace: bool = False,
) -> CorrelationIds:
    """Build the §51 id set; with ``issue_trace`` a fresh W3C pair is issued."""
    if issue_trace:
        trace_id = trace_id or new_trace_id()
        span_id = new_span_id()
    parent: str | None = None
    unresolved: list[str] = []
    if trace_id and span_id:
        bare = span_id.removeprefix("span:")
        try:
            parent = traceparent(_otlp_trace_id(trace_id), _otlp_span_id(bare))
        except ContractError as exc:
            unresolved.append(f"traceparent: {exc.detail}")
    else:
        unresolved.append("traceparent")
    names = {
        "task_id": task_id,
        "run_id": run_id,
        "trace_id": trace_id,
        "span_id": span_id,
        "agent_id": agent_id,
        "model_call_id": model_call_id,
        "tool_call_id": tool_call_id,
        "decision_id": decision_id,
        "memory_id": memory_id,
        "context_id": context_id,
    }
    unresolved.extend(name for name, value in names.items() if value is None)
    return CorrelationIds(
        task_id=task_id,
        run_id=run_id,
        trace_id=trace_id,
        span_id=span_id,
        agent_id=agent_id,
        model_call_id=model_call_id,
        tool_call_id=tool_call_id,
        decision_id=decision_id,
        memory_id=memory_id,
        context_id=context_id,
        traceparent=parent,
        unresolved=tuple(unresolved),
    )


def _otlp_trace_id(value: str) -> str:
    """Deterministic 32-hex trace id: pass through hex, hash free strings."""
    if len(value) == 32 and set(value.lower()) <= _HEX32:
        return value.lower()
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:32]


def _otlp_span_id(value: str) -> str:
    if len(value) == 16 and set(value.lower()) <= _HEX32:
        return value.lower()
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _unix_nanos(iso: str) -> tuple[int | None, str | None]:
    try:
        parsed = datetime.fromisoformat(iso)
    except ValueError:
        return None, f"unparseable timestamp {iso!r}"
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return int(parsed.timestamp() * 1_000_000_000), None


def _attr(key: str, value: object) -> dict[str, Any]:
    if isinstance(value, bool):
        return {"key": key, "value": {"boolValue": value}}
    if isinstance(value, int):
        return {"key": key, "value": {"intValue": str(value)}}
    if isinstance(value, (list, tuple)):
        items = [{"stringValue": str(item)} for item in value]
        return {"key": key, "value": {"arrayValue": {"values": items}}}
    return {"key": key, "value": {"stringValue": str(value)}}


def _span_to_otlp(span: AgentSpan, unresolved: list[str]) -> dict[str, Any]:
    start_ns, problem = _unix_nanos(span.started_at)
    if problem:
        unresolved.append(f"{span.span_id}: {problem}")
        start_ns = 0
    end_ns = None
    if span.ended_at:
        end_ns, problem = _unix_nanos(span.ended_at)
        if problem:
            unresolved.append(f"{span.span_id}: {problem}")
    attributes = [
        _attr("gen_ai.operation.name", span.operation),
        _attr("apiforge.operation", span.operation),
        _attr("apiforge.task_id", span.task_id),
        _attr("apiforge.run_id", span.run_id),
    ]
    for field in (
        "agent_id",
        "model_call_id",
        "tool_call_id",
        "decision_id",
        "memory_id",
        "context_id",
    ):
        value = getattr(span, field)
        if value is not None:
            attributes.append(_attr(f"apiforge.{field}", value))
    if span.agent_name is not None:
        attributes.append(_attr("gen_ai.agent.name", span.agent_name))
    if span.tool_name is not None:
        attributes.append(_attr("gen_ai.tool.name", span.tool_name))
    if span.unresolved:
        attributes.append(_attr("apiforge.unresolved", list(span.unresolved)))
    if span.evidence_refs:
        attributes.append(_attr("apiforge.evidence_refs", list(span.evidence_refs)))
    for key, value in sorted(span.attributes.items()):
        if isinstance(value, (str, int, bool, list, tuple)):
            attributes.append(_attr(str(key), value))
    status_code = {"unset": 0, "ok": 1, "error": 2, "unresolved": 0}[span.status]
    if span.status == "unresolved":
        attributes.append(_attr("apiforge.status_unresolved", True))
    otlp: dict[str, Any] = {
        "traceId": _otlp_trace_id(span.trace_id),
        "spanId": _otlp_span_id(span.span_id.removeprefix("span:")),
        "name": span.operation,
        "kind": 3 if span.operation in _CLIENT_OPERATIONS else 1,
        "startTimeUnixNano": str(start_ns),
        "attributes": attributes,
        "droppedAttributesCount": 0,
        "events": [
            {"timeUnixNano": str(start_ns), "name": name, "attributes": []} for name in span.events
        ],
        "droppedEventsCount": 0,
        "links": [],
        "droppedLinksCount": 0,
        "status": {"code": status_code, "message": span.status_message},
    }
    if end_ns is not None:
        otlp["endTimeUnixNano"] = str(end_ns)
    if span.parent_span_id:
        otlp["parentSpanId"] = _otlp_span_id(span.parent_span_id.removeprefix("span:"))
    return otlp


def to_otlp_payload(
    spans: list[AgentSpan] | tuple[AgentSpan, ...],
    *,
    service_name: str = "apiforge",
    unresolved: list[str] | None = None,
) -> dict[str, Any]:
    """Convert AgentSpan rows into one OTLP ExportTraceServiceRequest body."""
    problems: list[str] = [] if unresolved is None else unresolved
    converted = [_span_to_otlp(span, problems) for span in spans]
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [_attr("service.name", service_name)],
                    "droppedAttributesCount": 0,
                },
                "scopeSpans": [
                    {
                        "scope": {"name": _SCOPE_NAME, "version": _SCOPE_VERSION},
                        "spans": converted,
                        "schemaUrl": "",
                    }
                ],
                "schemaUrl": "",
            }
        ]
    }


def export_otlp(root: Path, *, service_name: str = "apiforge") -> OtlpExport:
    """Read the local span ledger and wrap the OTLP payload in a contract."""
    spans = _read(_directory(root))
    unresolved: list[str] = []
    payload = to_otlp_payload(spans, service_name=service_name, unresolved=unresolved)
    ledger = _directory(root) / "agent-spans.jsonl"
    return OtlpExport(
        service_name=service_name,
        span_count=len(spans),
        payload=payload,
        source_sha256=sha256_file(ledger) if ledger.is_file() else None,
        unresolved=tuple(unresolved),
    )


def validate_otlp(payload: object) -> OtlpValidation:
    """Deterministic §52 structural acceptance of an OTLP/JSON body."""
    problems: list[str] = []
    operations: set[str] = set()
    span_count = 0
    if not isinstance(payload, dict):
        problems.append("payload is not an object")
        return OtlpValidation(accepted=False, span_count=0, problems=tuple(problems))
    resource_spans = payload.get("resourceSpans")
    if not isinstance(resource_spans, (list, tuple)) or not resource_spans:
        problems.append("resourceSpans missing or empty")
        resource_spans = []
    for index, resource in enumerate(resource_spans):
        if not isinstance(resource, dict):
            problems.append(f"resourceSpans[{index}] is not an object")
            continue
        scopes = resource.get("scopeSpans")
        if not isinstance(scopes, (list, tuple)) or not scopes:
            problems.append(f"resourceSpans[{index}].scopeSpans missing or empty")
            continue
        for scope_index, scope in enumerate(scopes):
            spans = scope.get("spans") if isinstance(scope, dict) else None
            if not isinstance(spans, (list, tuple)):
                problems.append(f"scopeSpans[{scope_index}].spans missing")
                continue
            for span_index, span in enumerate(spans):
                at = f"spans[{span_index}]"
                if not isinstance(span, dict):
                    problems.append(f"{at} is not an object")
                    continue
                span_count += 1
                trace_id = span.get("traceId", "")
                if len(str(trace_id)) != 32 or not set(str(trace_id).lower()) <= _HEX32:
                    problems.append(f"{at}.traceId is not 32 hex chars")
                span_id = span.get("spanId", "")
                if len(str(span_id)) != 16 or not set(str(span_id).lower()) <= _HEX32:
                    problems.append(f"{at}.spanId is not 16 hex chars")
                if not str(span.get("startTimeUnixNano", "")).isdigit():
                    problems.append(f"{at}.startTimeUnixNano missing or not digits")
                if not span.get("name"):
                    problems.append(f"{at}.name missing")
                attrs = span.get("attributes")
                op = None
                if isinstance(attrs, (list, tuple)):
                    for attribute in attrs:
                        if isinstance(attribute, dict) and attribute.get("key") == (
                            "gen_ai.operation.name"
                        ):
                            op = attribute.get("value", {}).get("stringValue")
                if op is None:
                    problems.append(f"{at} lacks gen_ai.operation.name")
                else:
                    operations.add(str(op))
                status = span.get("status", {})
                if not isinstance(status, dict) or status.get("code") not in (0, 1, 2):
                    problems.append(f"{at}.status.code invalid")
    return OtlpValidation(
        accepted=not problems,
        span_count=span_count,
        problems=tuple(sorted(problems)),
        operations=tuple(sorted(operations)),
    )


def probe_collector(
    payload: dict[str, Any],
    *,
    endpoint: str,
    output_file: Path | None = None,
    timeout_s: float = 30.0,
) -> CollectorProbe:
    """§52 POST the payload to a real OTLP/HTTP collector and count accepts.

    ``output_file`` is the collector's file-exporter path; acceptance means
    at least ``sent`` span ids appear in it within ``timeout_s``.
    """
    sent = sum(
        len(scope.get("spans", []))
        for resource in payload.get("resourceSpans", [])
        for scope in resource.get("scopeSpans", [])
        if isinstance(scope, dict)
    )
    span_ids = {
        str(span.get("spanId"))
        for resource in payload.get("resourceSpans", [])
        for scope in resource.get("scopeSpans", [])
        if isinstance(scope, dict)
        for span in scope.get("spans", [])
        if isinstance(span, dict)
    }
    url = endpoint.rstrip("/") + "/v1/traces"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status >= 400:
                return CollectorProbe(
                    endpoint=url,
                    sent=sent,
                    accepted=0,
                    status="refused",
                    detail=f"collector answered HTTP {response.status}",
                    code=COLLECTOR_REFUSED_CODE,
                )
    except urllib.error.HTTPError as exc:
        return CollectorProbe(
            endpoint=url,
            sent=sent,
            accepted=0,
            status="refused",
            detail=f"collector refused: HTTP {exc.code}",
            code=COLLECTOR_REFUSED_CODE,
        )
    except OSError as exc:
        return CollectorProbe(
            endpoint=url,
            sent=sent,
            status="unresolved",
            detail=f"collector unreachable: {exc}",
            code=COLLECTOR_UNRESOLVED_CODE,
            unresolved=("endpoint",),
        )
    if output_file is None:
        return CollectorProbe(
            endpoint=url,
            sent=sent,
            status="unresolved",
            detail="posted but no collector output file declared to confirm acceptance",
            unresolved=("output_file",),
        )
    deadline = time.monotonic() + timeout_s
    found: set[str] = set()
    while time.monotonic() < deadline:
        if output_file.is_file():
            text = output_file.read_text(encoding="utf-8", errors="replace")
            found = {span_id for span_id in span_ids if span_id in text}
            if len(found) >= len(span_ids):
                break
        time.sleep(0.25)
    if len(found) >= len(span_ids) and span_ids:
        return CollectorProbe(endpoint=url, sent=sent, accepted=len(found), status="accepted")
    return CollectorProbe(
        endpoint=url,
        sent=sent,
        accepted=len(found),
        status="refused",
        detail=f"only {len(found)}/{len(span_ids)} span ids reached the output file",
        code=COLLECTOR_TIMEOUT_CODE,
    )


__all__ = [
    "COLLECTOR_REFUSED_CODE",
    "COLLECTOR_TIMEOUT_CODE",
    "COLLECTOR_UNRESOLVED_CODE",
    "EXPORT_INVALID_CODE",
    "TRACEPARENT_INVALID_CODE",
    "correlation_ids",
    "export_otlp",
    "new_span_id",
    "new_trace_id",
    "parse_traceparent",
    "probe_collector",
    "to_otlp_payload",
    "traceparent",
    "validate_otlp",
]
