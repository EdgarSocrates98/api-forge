from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from apiforge.contracts.agent_telemetry import AgentSpanQuery
from apiforge.mcp import tools
from apiforge.runtime.agent_telemetry import append_span, build_span, query_spans


def test_sensitive_attribute_is_rejected() -> None:
    with pytest.raises(ValidationError, match="AF-OTEL-SENSITIVE-ATTRIBUTE"):
        build_span(
            trace_id="trace-1", task_id="task-1", run_id="run-1", operation="execute_tool",
            started_at="2026-10-04T12:00:00Z", tool_name="shell",
            attributes={"authorization": "never-store"},
        )


def test_append_query_and_idempotency(tmp_path: Path) -> None:
    span = build_span(
        trace_id="trace-1", task_id="task-1", run_id="run-1", operation="execute_tool",
        started_at="2026-10-04T12:00:00Z", ended_at="2026-10-04T12:00:01Z", status="ok",
        tool_name="budget_check", attributes={"gen_ai.tool.name": "budget_check"},
    )
    assert append_span(tmp_path, span)["status"] == "accepted"
    assert append_span(tmp_path, span)["status"] == "deduplicated"
    result = query_spans(tmp_path, AgentSpanQuery(trace_id="trace-1"))
    assert result.status == "ready"
    assert len(result.spans) == 1


def test_mcp_span_projection_uses_same_store(tmp_path: Path) -> None:
    appended = tools.agent_span_append(
        trace_id="trace-mcp", task_id="task-mcp", run_id="run-mcp", operation="invoke_agent",
        started_at="2026-10-04T12:00:00Z", root=str(tmp_path), agent_name="reviewer",
        attributes={"gen_ai.agent.name": "reviewer"},
    )
    assert appended["status"] == "accepted"
    queried = tools.agent_span_query(root=str(tmp_path), trace_id="trace-mcp")
    assert queried["status"] == "ready"
    assert len(queried["spans"]) == 1
