"""§53–§54 run inspection: one structured report over every run ledger.

Every metric carries its evidence basis; a section whose source ledger is
absent still appears with its metrics unresolved — sections are never
silently dropped.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from apiforge.agentops.waste import detect_waste
from apiforge.contracts.agentops_report import (
    InspectionMetric,
    InspectionSection,
    RunInspection,
)
from apiforge.economy import run_ledger, token_ledger
from apiforge.runtime.agent_telemetry import _directory as span_dir
from apiforge.runtime.agent_telemetry import _read as read_spans

_DECISION_GATES = Path(".apiforge") / "governance" / "decision-gates.jsonl"
_MEMORY_DIR = Path(".apiforge") / "memory"
_DECISION_OPS = {"decision", "security_decision", "promotion"}


def _span_duration_ms(span: object) -> int | None:
    """Read declared span duration; missing timestamps never become zero."""
    attributes = getattr(span, "attributes", {})
    declared = attributes.get("duration_ms") if hasattr(attributes, "get") else None
    if isinstance(declared, (int, float)) and declared >= 0:
        return round(float(declared))
    started = getattr(span, "started_at", None)
    ended = getattr(span, "ended_at", None)
    if not isinstance(started, str) or not isinstance(ended, str):
        return None
    try:
        start = datetime.fromisoformat(started)
        finish = datetime.fromisoformat(ended)
    except ValueError:
        return None
    duration = (finish - start).total_seconds() * 1000
    return round(duration) if duration >= 0 else None


def _metric(
    name: str, value: object, state: str = "observed", detail: str = ""
) -> InspectionMetric:
    if state == "unresolved":
        value = None
    return InspectionMetric(name=name, value=value, state=state, detail=detail)  # type: ignore[arg-type]


def _unresolved(name: str, detail: str) -> InspectionMetric:
    return InspectionMetric(name=name, value=None, state="unresolved", detail=detail)


def _count_jsonl(path: Path, field: str | None = None) -> tuple[int, dict[str, int]]:
    if not path.is_file():
        return 0, {}
    total = 0
    by_value: Counter[str] = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        total += 1
        if field:
            by_value[str(row.get(field, ""))] += 1
    return total, dict(by_value)


def inspect_run(root: Path, run_id: str, *, risk: str | None = None) -> RunInspection:
    """Aggregate one run's ledgers into the §54 sectioned report."""
    root = Path(root)
    unresolved: list[str] = []

    entries, _legacy = run_ledger.entries(root)
    rows = [entry for entry in entries if entry.run_id == run_id]
    spans = [span for span in read_spans(span_dir(root)) if span.run_id == run_id]
    usage = token_ledger.load_entries(root, run_id)[0]
    if not rows and not spans and not usage:
        unresolved.append("no ledger rows, spans or token usage for this run")

    from apiforge.context.quality import evaluate, uses_from_ledger

    uses = uses_from_ledger(root, run_id)
    report = evaluate((), uses, run_id=run_id)
    metrics = {str(metric.name): metric for metric in report.metrics}

    task_ids = sorted(
        {row.task_id for row in usage if row.task_id} | {span.task_id for span in spans}
    )
    task_id = task_ids[0] if len(task_ids) == 1 else None
    if len(task_ids) > 1:
        unresolved.append("multiple task_ids observed in run")

    # --- agents: invocation/debate/review/retry shapes from spans.
    op_counts = Counter(span.operation for span in spans)
    agents = sorted(
        {span.agent_name for span in spans if span.agent_name}
        | {row.agent for row in usage if row.agent}
    )
    agent_section = InspectionSection(
        name="agents",
        metrics=(
            _metric("agents", len(agents), detail=", ".join(agents) if agents else ""),
            _metric("invocations", op_counts.get("invoke_agent", 0)),
            _metric("reviews", op_counts.get("review", 0)),
            _metric("debates", op_counts.get("debate", 0)),
            _metric("handoffs", op_counts.get("handoff", 0)),
            _metric("resumes", op_counts.get("resume", 0)),
            _metric("retries", sum(row.cost.expansions for row in rows)),
        ),
    )

    # --- context: bytes, tokens, precision/recall/density, cache, reuse.
    context_bytes = sum(row.cost.context_bytes for row in rows)
    cache_hits = sum(row.cost.cache_hits for row in rows)

    def _q(name: str) -> InspectionMetric:
        metric = metrics.get(name)
        if metric is None:
            return _unresolved(name, "metric not emitted by context quality")
        if metric.basis == "unresolved":
            return _unresolved(name, metric.detail)
        return _metric(name, metric.value, detail=metric.detail or metric.basis)

    observed_context_tokens = [row.cost.observed_tokens for row in rows if row.cost.observed_tokens is not None]
    token_eligible_rows = len(rows)
    if not token_eligible_rows:
        context_tokens = _unresolved("tokens", "no run-ledger rows are available for token observation")
        token_coverage = _unresolved(
            "token_observation_coverage", "token-eligible row denominator is unknown"
        )
    else:
        token_coverage = _metric(
            "token_observation_coverage",
            len(observed_context_tokens) / token_eligible_rows,
            detail=(
                f"{len(observed_context_tokens)}/{token_eligible_rows} run-ledger rows carry observed tokens"
            ),
        )
        if not observed_context_tokens:
            context_tokens = _unresolved(
                "tokens", "no run-ledger rows carry observed token usage"
            )
        else:
            context_tokens = _metric(
                "tokens",
                sum(observed_context_tokens),
                "observed" if len(observed_context_tokens) == token_eligible_rows else "partial",
                detail=(
                    "all token-eligible rows carry observed tokens"
                    if len(observed_context_tokens) == token_eligible_rows
                    else "only a subset of token-eligible rows carry observed tokens"
                ),
            )

    context_section = InspectionSection(
        name="context",
        metrics=(
            _metric("bytes", context_bytes),
            context_tokens,
            token_coverage,
            _q("context_precision"),
            _q("context_recall"),
            _q("context_density"),
            _q("duplicate_context_ratio"),
            _q("stale_context_ratio"),
            _metric("cache_hits", cache_hits),
            _metric("reuse", sum(1 for use in uses if use.action in ("cited", "artifact"))),
        ),
    )

    # --- memory: store-wide counts; per-run attribution is unresolved.
    memory_dir = root / _MEMORY_DIR
    candidates, _ = _count_jsonl(memory_dir / "candidates.jsonl")
    records, by_outcome = _count_jsonl(memory_dir / "records.jsonl", "outcome")
    invalidated, _ = _count_jsonl(memory_dir / "invalidations.jsonl")
    quarantined, _ = _count_jsonl(memory_dir / "quarantine.jsonl")
    memory_state = "unresolved" if not memory_dir.is_dir() else "estimated"
    memory_detail = (
        "store-wide; memory rows carry no run_id"
        if memory_dir.is_dir()
        else "no memory store present"
    )
    memory_section = InspectionSection(
        name="memory",
        metrics=(
            _metric("records", records, memory_state, memory_detail),
            _metric("candidates", candidates, memory_state, memory_detail),
            _metric("accepted", by_outcome.get("accepted", 0), memory_state, memory_detail),
            _metric("rejected", by_outcome.get("rejected", 0), memory_state, memory_detail),
            _metric("quarantined", quarantined, memory_state, memory_detail),
            _metric("invalidated", invalidated, memory_state, memory_detail),
        ),
    )
    if memory_state == "unresolved":
        unresolved.append("memory store absent — section unresolved")
    elif memory_state == "estimated":
        unresolved.append("memory metrics are store-wide; per-run attribution unresolved")

    # --- tools: calls, failures, output bytes.
    tool_bytes = sum(row.cost.tool_result_bytes for row in rows)
    failures = sum(1 for span in spans if span.status == "error")
    tools_section = InspectionSection(
        name="tools",
        metrics=(
            _metric("calls", len(rows)),
            _metric("failures", failures),
            _metric("output_bytes", tool_bytes),
        ),
    )

    # --- models: calls, provider attempts, token usage and latency stay separate.
    totals: dict[str, dict[str, int]] = {"observed": {}, "estimated": {}}
    for entry in usage:
        acc = entry.accounting
        if acc.basis == "unresolved":
            continue
        bucket = totals[acc.basis]
        for field in ("input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens"):
            value = getattr(acc, field)
            if value is not None:
                bucket[field] = bucket.get(field, 0) + value
    model_spans = [span for span in spans if span.operation == "invoke_model"]
    model_call_ids = {entry.model_call_id for entry in usage if entry.model_call_id}
    model_call_ids.update(span.model_call_id for span in model_spans if span.model_call_id)
    if model_call_ids:
        model_calls = _metric(
            "calls",
            len(model_call_ids),
            detail="unique model_call_id values across token ledger and model spans",
        )
    elif usage or model_spans:
        model_calls = _unresolved(
            "calls",
            "model_call_id is absent; token rows cannot be counted as model calls",
        )
        unresolved.append("model-call count unresolved — model_call_id missing")
    else:
        model_calls = _unresolved("calls", "no token or invoke_model evidence")
    if model_spans:
        provider_attempts = _metric(
            "provider_attempts",
            len(model_spans),
            detail="invoke_model spans; retries remain distinct attempts",
        )
        durations = [_span_duration_ms(span) for span in model_spans]
        if all(duration is not None for duration in durations):
            model_latency = _metric(
                "model_latency_ms",
                sum(duration for duration in durations if duration is not None),
                detail="sum of invoke_model span durations",
            )
        else:
            model_latency = _unresolved(
                "model_latency_ms",
                "one or more invoke_model spans lack a valid duration",
            )
    else:
        provider_attempts = _unresolved("provider_attempts", "no invoke_model spans recorded")
        model_latency = _unresolved("model_latency_ms", "no invoke_model spans recorded")
    models_section = InspectionSection(
        name="models",
        metrics=(
            model_calls,
            provider_attempts,
            _metric("token_entries", len(usage)),
            _metric(
                "input_tokens",
                totals["observed"].get("input_tokens"),
                "observed" if totals["observed"].get("input_tokens") is not None else "unresolved",
                "token ledger carries observed input"
                if totals["observed"].get("input_tokens") is not None
                else "no observed input tokens recorded",
            ),
            _metric(
                "output_tokens",
                totals["observed"].get("output_tokens"),
                "observed" if totals["observed"].get("output_tokens") is not None else "unresolved",
                "token ledger carries observed output"
                if totals["observed"].get("output_tokens") is not None
                else "no observed output tokens recorded",
            ),
            _metric(
                "cached_tokens",
                totals["observed"].get("cached_input_tokens"),
                "observed"
                if totals["observed"].get("cached_input_tokens") is not None
                else "unresolved",
                "provider-reported cache reads"
                if totals["observed"].get("cached_input_tokens") is not None
                else "no cached tokens recorded",
            ),
            _metric(
                "estimated_tokens",
                totals["estimated"].get("input_tokens"),
                "estimated"
                if totals["estimated"].get("input_tokens") is not None
                else "unresolved",
                "estimator-declared tokens"
                if totals["estimated"].get("input_tokens") is not None
                else "no estimated token rows",
            ),
            _unresolved("cost", "provider cost requires declared pricing — use economy cost"),
            model_latency,
            _metric(
                "run_latency_ms",
                sum(row.cost.duration_ms for row in rows),
                detail="sum of run-ledger durations; never presented as model latency",
            ),
        ),
    )

    # --- evidence: facts/findings coverage + unresolved.
    evidence_refs = sorted(
        {ref for span in spans for ref in span.evidence_refs}
        | {ref.uri for row in rows for ref in row.refs}
    )
    span_unresolved = sorted({item for span in spans for item in span.unresolved})
    evidence_section = InspectionSection(
        name="evidence",
        metrics=(
            _metric("refs", len(evidence_refs)),
            _metric("unresolved_items", len(span_unresolved)),
        ),
    )

    # --- security: decision gate rows for this run.
    gates_path = root / _DECISION_GATES
    allowed = blocked = 0
    gate_runs = 0
    if gates_path.is_file():
        for line in gates_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                gate = json.loads(line)
            except json.JSONDecodeError:
                continue
            if gate.get("run_id") != run_id:
                continue
            gate_runs += 1
            outcome = gate.get("outcome")
            if outcome == "allow" or (outcome is None and gate.get("allowed") is True):
                allowed += 1
            elif outcome == "block" or (outcome is None and gate.get("allowed") is False):
                blocked += 1
    else:
        unresolved.append("decision-gates ledger absent — security section unresolved")
    trust_violations = sum(
        1 for span in spans if span.operation == "security_decision" and span.status == "error"
    )
    security_section = InspectionSection(
        name="security",
        metrics=(
            _metric(
                "decisions",
                gate_runs,
                "observed" if gates_path.is_file() else "unresolved",
                "" if gates_path.is_file() else "decision-gates ledger absent",
            ),
            _metric(
                "allowed",
                allowed,
                "observed" if gates_path.is_file() else "unresolved",
                "" if gates_path.is_file() else "decision-gates ledger absent",
            ),
            _metric(
                "blocked",
                blocked,
                "observed" if gates_path.is_file() else "unresolved",
                "" if gates_path.is_file() else "decision-gates ledger absent",
            ),
            _metric(
                "review",
                gate_runs - allowed - blocked,
                "observed" if gates_path.is_file() else "unresolved",
                "" if gates_path.is_file() else "decision-gates ledger absent",
            ),
            _metric("trust_violations", trust_violations),
        ),
    )

    # --- decision path: ordered span operations that govern.
    decision_path = tuple(
        f"{span.operation}:{span.status}" for span in spans if span.operation in _DECISION_OPS
    )

    waste = detect_waste(root, run_id, risk=risk)
    unresolved.extend(waste.unresolved)

    run_section = InspectionSection(
        name="run",
        metrics=(
            _metric("run_id", run_id),
            _metric(
                "task_id",
                task_id,
                "observed" if task_id else "unresolved",
                detail="" if task_id else "no task_id recorded for this run",
            ),
            _metric("entries", len(rows)),
            _metric("spans", len(spans)),
            _metric("token_entries", len(usage)),
        ),
    )

    return RunInspection(
        run_id=run_id,
        task_id=task_id,
        profile=None,
        risk=risk,
        sections=(
            run_section,
            agent_section,
            context_section,
            memory_section,
            tools_section,
            models_section,
            evidence_section,
            security_section,
        ),
        waste=waste.findings,
        decision_path=decision_path,
        unresolved=tuple(unresolved),
    )


__all__ = ["inspect_run"]
