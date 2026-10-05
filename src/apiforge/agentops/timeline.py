"""Cross-ledger AgentOps timeline projection."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.agentops_report import AgentOpsTimeline, AgentOpsTimelineEvent
from apiforge.economy import run_ledger, token_ledger
from apiforge.runtime.agent_telemetry import _directory, _read


def build_timeline(root: Path, run_id: str) -> AgentOpsTimeline:
    """Merge local ledger, span and token evidence without inventing timestamps."""
    events: list[AgentOpsTimelineEvent] = []
    unresolved: list[str] = []
    rows, _ = run_ledger.entries(root)
    run_rows = [row for row in rows if row.run_id == run_id]
    for index, row in enumerate(run_rows):
        events.append(
            AgentOpsTimelineEvent(
                event_id=f"ledger:{index}",
                source="ledger",
                operation=row.verb,
                status="observed",
                detail=f"{len(row.refs)} ref(s)",
            )
        )
    if run_rows:
        unresolved.append(
            "ledger rows lack timestamps; append order retained after timestamped events"
        )

    spans = [span for span in _read(_directory(root)) if span.run_id == run_id]
    for span in spans:
        events.append(
            AgentOpsTimelineEvent(
                event_id=span.span_id,
                source="span",
                operation=span.operation,
                timestamp=span.started_at,
                status=span.status,
                detail=span.tool_name or span.agent_name or "",
            )
        )

    usage = token_ledger.load_entries(root, run_id)[0]
    for entry in usage:
        events.append(
            AgentOpsTimelineEvent(
                event_id=f"token:{entry.entry_id}",
                source="token",
                operation="model",
                timestamp=entry.recorded_at,
                status=entry.accounting.basis,
                detail=entry.accounting.model or "model unresolved",
            )
        )

    source_order = {"span": 0, "token": 1, "ledger": 2}
    events.sort(
        key=lambda event: (
            event.timestamp is None,
            event.timestamp or "",
            source_order[event.source],
            event.event_id,
        )
    )
    if not events:
        unresolved.append("no ledger, span or token events for this run")
    return AgentOpsTimeline(run_id=run_id, events=tuple(events), unresolved=tuple(unresolved))


__all__ = ["build_timeline"]
