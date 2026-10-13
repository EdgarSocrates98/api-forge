from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.contracts.agent_telemetry import AgentSpanQuery, CorrelationIds
from apiforge.contracts.base import ContractError
from apiforge.runtime.agent_telemetry import append_span, build_span, query_spans
from apiforge.runtime.otel_export import (
    correlation_ids,
    export_otlp,
    new_span_id,
    new_trace_id,
    parse_traceparent,
    probe_collector,
    to_otlp_payload,
    traceparent,
    validate_otlp,
)


def _span(**over: object) -> object:
    base: dict[str, object] = {
        "trace_id": "trace-ot-1",
        "task_id": "task-1",
        "run_id": "run-1",
        "operation": "invoke_model",
        "started_at": "2026-10-06T10:00:00Z",
        "ended_at": "2026-10-06T10:00:01Z",
        "status": "ok",
    }
    base.update(over)
    return build_span(**base)  # type: ignore[arg-type]


def test_traceparent_round_trip_and_refusals() -> None:
    trace, span = new_trace_id(), new_span_id()
    value = traceparent(trace, span)
    parsed_trace, parsed_span, sampled = parse_traceparent(value)
    assert (parsed_trace, parsed_span, sampled) == (trace, span, True)
    with pytest.raises(ContractError, match="AF-OTEL-TRACEPARENT-INVALID"):
        traceparent("not-hex", span)
    with pytest.raises(ContractError, match="AF-OTEL-TRACEPARENT-INVALID"):
        parse_traceparent("00-zz-7bc9113136bcba66-01")


def test_correlation_ids_issues_trace_and_names_unresolved() -> None:
    ids = correlation_ids(task_id="t1", issue_trace=True)
    assert isinstance(ids, CorrelationIds)
    assert ids.traceparent and ids.traceparent.startswith("00-")
    assert "task_id" not in ids.unresolved
    assert "run_id" in ids.unresolved and "memory_id" in ids.unresolved


def test_to_otlp_payload_shape_and_semconv() -> None:
    span = _span(
        decision_id="dec-9",
        memory_id="mem-2",
        tool_name="budget_check",
        unresolved=("price",),
    )
    problems: list[str] = []
    payload = to_otlp_payload([span], unresolved=problems)  # type: ignore[list-item]
    resource = payload["resourceSpans"][0]
    scope = resource["scopeSpans"][0]
    otlp_span = scope["spans"][0]
    assert len(otlp_span["traceId"]) == 32
    assert len(otlp_span["spanId"]) == 16
    assert otlp_span["name"] == "invoke_model"
    assert otlp_span["kind"] == 3  # model call is a client span
    assert otlp_span["status"]["code"] == 1
    keys = {a["key"] for a in otlp_span["attributes"]}
    assert "gen_ai.operation.name" in keys
    assert "gen_ai.tool.name" in keys
    assert "apiforge.decision_id" in keys and "apiforge.memory_id" in keys
    assert "apiforge.unresolved" in keys
    assert problems == []


def test_export_otlp_reads_ledger_and_validates(tmp_path: Path) -> None:
    append_span(tmp_path, _span())  # type: ignore[arg-type]
    append_span(tmp_path, _span(operation="execute_tool", tool_name="x"))  # type: ignore[arg-type]
    export = export_otlp(tmp_path)
    assert export.span_count == 2
    validation = validate_otlp(export.payload)
    assert validation.accepted
    assert validation.span_count == 2
    assert set(validation.operations) == {"invoke_model", "execute_tool"}


def test_validate_otlp_refuses_malformed() -> None:
    bad = validate_otlp({"resourceSpans": [{"scopeSpans": [{"spans": [{"traceId": "x"}]}]}]})
    assert not bad.accepted
    assert any("traceId" in problem for problem in bad.problems)
    empty = validate_otlp({"resourceSpans": []})
    assert not empty.accepted


def test_all_section50_operations_are_valid(tmp_path: Path) -> None:
    ops = (
        "task",
        "routing",
        "context_build",
        "context_expansion",
        "retrieval",
        "memory_read",
        "memory_write",
        "invoke_agent",
        "invoke_model",
        "execute_tool",
        "handoff",
        "review",
        "debate",
        "security_decision",
        "decision",
        "checkpoint",
        "resume",
        "promotion",
    )
    for op in ops:
        append_span(tmp_path, _span(operation=op))  # type: ignore[arg-type]
    export = export_otlp(tmp_path)
    validation = validate_otlp(export.payload)
    assert validation.accepted
    assert set(validation.operations) == set(ops)
    assert export.span_count == 18


def test_probe_collector_unreachable_is_unresolved(tmp_path: Path) -> None:
    payload = to_otlp_payload([_span()])  # type: ignore[list-item]
    probe = probe_collector(payload, endpoint="http://127.0.0.1:9", output_file=tmp_path / "o.json")
    assert probe.status == "unresolved"
    assert probe.code == "AF-OTEL-COLLECTOR-UNRESOLVED"


def test_probe_collector_accepts_when_ids_reach_output(tmp_path: Path) -> None:
    import http.server
    import threading

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)
            self.send_response(200)
            self.end_headers()

        def log_message(self, *_: object) -> None:
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        payload = to_otlp_payload([_span(), _span(operation="review")])  # type: ignore[list-item]
        span_ids = {
            s["spanId"]
            for r in payload["resourceSpans"]
            for sc in r["scopeSpans"]
            for s in sc["spans"]
        }
        out = tmp_path / "spans.json"
        out.write_text("\n".join(sorted(span_ids)), encoding="utf-8")
        probe = probe_collector(
            payload, endpoint=f"http://127.0.0.1:{server.server_port}", output_file=out
        )
        assert probe.status == "accepted"
        assert probe.accepted == 2
    finally:
        server.shutdown()


def test_query_spans_still_filters_after_contract_extension(tmp_path: Path) -> None:
    append_span(tmp_path, _span(operation="memory_read"))  # type: ignore[arg-type]
    result = query_spans(tmp_path, AgentSpanQuery(operation="memory_read"))
    assert len(result.spans) == 1
    other = query_spans(tmp_path, AgentSpanQuery(operation="promotion"))
    assert len(other.spans) == 0


def test_json_serializable_contracts(tmp_path: Path) -> None:
    append_span(tmp_path, _span())  # type: ignore[arg-type]
    export = export_otlp(tmp_path)
    json.dumps(export.model_dump(mode="json"))
    json.dumps(export.payload)
