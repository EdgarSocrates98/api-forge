"""Phase 8 §53–§57: inspect, compare and the waste detector over local ledgers."""

import json
from pathlib import Path

import pytest

from apiforge.agentops.compare import compare_runs
from apiforge.agentops.inspect import inspect_run
from apiforge.agentops.waste import detect_waste
from apiforge.contracts.base import ContractError
from apiforge.contracts.economy import CostVector, LedgerRef, RunLedgerEntry
from apiforge.contracts.token_economics import TokenLedgerEntry
from apiforge.economy import run_ledger, token_ledger
from apiforge.economy.token_ledger import entry_id, transcript_accounting
from apiforge.runtime.agent_telemetry import append_span, build_span


def _ref(name: str, size: int = 10) -> LedgerRef:
    return LedgerRef(
        uri="ctx://sha256/" + name * 64,
        label=f"schema:{name}",
        provenance="schema-ref",
        size_bytes=size,
    )


def _row(
    run_id: str,
    verb: str = "context capsule",
    *,
    refs: tuple[LedgerRef, ...] = (),
    cost: CostVector | None = None,
    source: str = "contract",
) -> RunLedgerEntry:
    return RunLedgerEntry(
        run_id=run_id,
        verb=verb,
        source=source,  # type: ignore[arg-type]
        cost=cost or CostVector(),
        refs=refs,
    )


def _usage(
    root: Path,
    run_id: str,
    agent: str = "builder",
    model: str = "m1",
    model_call_id: str | None = "model-call-1",
) -> None:
    accounting = transcript_accounting(
        model, {"input_tokens": 100, "output_tokens": 50}, recorded="t0"
    )
    token_ledger.append_usage(
        root,
        TokenLedgerEntry(
            run_id=run_id,
            agent=agent,
            accounting=accounting,
            entry_id=entry_id(run_id, accounting, "t0"),
            recorded_at="t0",
            model_call_id=model_call_id,
        ),
    )


def _seed_basic(root: Path, run_id: str) -> None:
    run_ledger.append(
        root,
        _row(
            run_id,
            refs=(_ref("a"), _ref("b")),
            cost=CostVector(context_bytes=500, cache_hits=2, duration_ms=120, observed_tokens=300),
        ),
    )
    _usage(root, run_id)


# --- inspect ---------------------------------------------------------------


def test_inspect_missing_run_names_unresolved(tmp_path: Path) -> None:
    report = inspect_run(tmp_path, "ghost")
    section_names = [section.name for section in report.sections]
    assert section_names == [
        "run",
        "agents",
        "context",
        "memory",
        "tools",
        "models",
        "evidence",
        "security",
    ]
    assert "no ledger rows, spans or token usage" in report.unresolved[0]
    for section in report.sections:
        for metric in section.metrics:
            if metric.state == "unresolved":
                assert metric.value is None
                assert metric.detail


def test_inspect_observed_metrics(tmp_path: Path) -> None:
    _seed_basic(tmp_path, "run-1")
    report = inspect_run(tmp_path, "run-1")

    def value(section: str, name: str) -> object:
        for item in report.sections:
            if item.name == section:
                for metric in item.metrics:
                    if metric.name == name:
                        return metric.value
        raise AssertionError(f"{section}.{name} missing")

    assert value("context", "bytes") == 500
    assert value("context", "tokens") == 300
    assert value("context", "cache_hits") == 2
    assert value("models", "calls") == 1
    assert value("models", "input_tokens") == 100
    assert value("agents", "agents") == 1
    # precision/recall have no capsule basis — unresolved, not zero.
    for section in report.sections:
        if section.name == "context":
            states = {m.name: m.state for m in section.metrics}
    assert states["context_precision"] == "unresolved"


def test_inspect_memory_and_security_sections_unresolved_without_stores(
    tmp_path: Path,
) -> None:
    _seed_basic(tmp_path, "run-1")
    report = inspect_run(tmp_path, "run-1")
    assert any("memory store absent" in item for item in report.unresolved)


def test_inspect_deterministic(tmp_path: Path) -> None:
    _seed_basic(tmp_path, "run-1")
    first = inspect_run(tmp_path, "run-1")
    second = inspect_run(tmp_path, "run-1")
    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_inspect_separates_model_calls_attempts_and_latencies(tmp_path: Path) -> None:
    _usage(tmp_path, "run-1", model_call_id="model-call-1")
    second = transcript_accounting("m1", {"input_tokens": 20}, recorded="t1")
    token_ledger.append_usage(
        tmp_path,
        TokenLedgerEntry(
            run_id="run-1",
            entry_id=entry_id("run-1", second, "t1", model_call_id="model-call-1"),
            recorded_at="t1",
            model_call_id="model-call-1",
            accounting=second,
        ),
    )
    append_span(
        tmp_path,
        build_span(
            trace_id="trace-1",
            task_id="task-1",
            run_id="run-1",
            operation="invoke_model",
            model_call_id="model-call-1",
            started_at="2026-10-05T12:00:00Z",
            ended_at="2026-10-05T12:00:00.125Z",
        ),
    )
    models = next(
        section for section in inspect_run(tmp_path, "run-1").sections if section.name == "models"
    )
    values = {metric.name: metric for metric in models.metrics}
    assert values["calls"].value == 1
    assert values["provider_attempts"].value == 1
    assert values["token_entries"].value == 2
    assert values["model_latency_ms"].value == 125
    assert values["run_latency_ms"].value == 0


def test_inspect_gate_outcomes_keep_review_distinct_from_block(tmp_path: Path) -> None:
    gate_path = tmp_path / ".apiforge" / "governance" / "decision-gates.jsonl"
    gate_path.parent.mkdir(parents=True)
    rows = [
        {"run_id": "run-1", "outcome": "allow"},
        {"run_id": "run-1", "outcome": "review"},
        {"run_id": "run-1", "outcome": "block"},
    ]
    gate_path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    security = next(
        section for section in inspect_run(tmp_path, "run-1").sections if section.name == "security"
    )
    values = {metric.name: metric.value for metric in security.metrics}
    assert values["decisions"] == 3
    assert values["allowed"] == 1
    assert values["review"] == 1
    assert values["blocked"] == 1


def test_inspect_missing_model_correlation_is_unresolved(tmp_path: Path) -> None:
    _usage(tmp_path, "run-1", model_call_id=None)
    models = next(
        section for section in inspect_run(tmp_path, "run-1").sections if section.name == "models"
    )
    calls = next(metric for metric in models.metrics if metric.name == "calls")
    assert calls.value is None
    assert calls.state == "unresolved"


def test_inspect_context_tokens_without_observation_are_unresolved(tmp_path: Path) -> None:
    run_ledger.append(tmp_path, _row("run-1", cost=CostVector(context_bytes=10)))
    context = next(
        section for section in inspect_run(tmp_path, "run-1").sections if section.name == "context"
    )
    metrics = {metric.name: metric for metric in context.metrics}
    assert metrics["tokens"].value is None
    assert metrics["tokens"].state == "unresolved"
    assert metrics["token_observation_coverage"].value == 0.0


def test_inspect_context_tokens_expose_partial_coverage(tmp_path: Path) -> None:
    run_ledger.append(tmp_path, _row("run-1", cost=CostVector(observed_tokens=300)))
    run_ledger.append(tmp_path, _row("run-1", cost=CostVector()))
    context = next(
        section for section in inspect_run(tmp_path, "run-1").sections if section.name == "context"
    )
    metrics = {metric.name: metric for metric in context.metrics}
    assert metrics["tokens"].value == 300
    assert metrics["tokens"].state == "partial"
    assert metrics["token_observation_coverage"].value == 0.5


# --- compare ---------------------------------------------------------------


def test_compare_picks_lower_context_bytes(tmp_path: Path) -> None:
    run_ledger.append(
        tmp_path,
        _row("run-a", cost=CostVector(context_bytes=400, observed_tokens=200)),
    )
    run_ledger.append(
        tmp_path,
        _row("run-b", cost=CostVector(context_bytes=900, observed_tokens=200)),
    )
    result = compare_runs(tmp_path, "run-a", "run-b")
    verdicts = {axis.axis: axis.verdict for axis in result.axes}
    assert verdicts["context"] == "a"
    assert verdicts["tokens"] == "tie"
    assert verdicts["cost"] == "unresolved"  # no pricing data on either side


def test_compare_unresolved_axis_never_ties(tmp_path: Path) -> None:
    _seed_basic(tmp_path, "run-a")
    result = compare_runs(tmp_path, "run-a", "ghost")
    quality = next(axis for axis in result.axes if axis.axis == "quality")
    assert quality.verdict == "unresolved"
    assert any(item.startswith("axis quality") for item in result.unresolved)


def test_compare_axis_set_complete(tmp_path: Path) -> None:
    _seed_basic(tmp_path, "run-a")
    _seed_basic(tmp_path, "run-b")
    result = compare_runs(tmp_path, "run-a", "run-b")
    assert {axis.axis for axis in result.axes} == {
        "quality",
        "tokens",
        "cost",
        "latency",
        "context",
        "evidence",
        "tools",
        "agents",
    }


# --- waste -----------------------------------------------------------------


def test_waste_duplicate_context_observed(tmp_path: Path) -> None:
    run_ledger.append(tmp_path, _row("run-1", refs=(_ref("a"), _ref("a"))))
    report = detect_waste(tmp_path, "run-1")
    kinds = {finding.kind: finding.evidence for finding in report.findings}
    assert kinds["duplicate_context"] == "observed"


def test_waste_duplicate_retrieval_observed(tmp_path: Path) -> None:
    run_ledger.append(
        tmp_path, _row("run-1", "context expand", source="knowledge", refs=(_ref("a"),))
    )
    run_ledger.append(
        tmp_path, _row("run-1", "context expand", source="knowledge", refs=(_ref("a"),))
    )
    report = detect_waste(tmp_path, "run-1")
    kinds = {finding.kind for finding in report.findings}
    assert "duplicate_retrieval" in kinds


def test_waste_empty_run_has_no_findings_but_report(tmp_path: Path) -> None:
    report = detect_waste(tmp_path, "ghost")
    assert report.findings == ()
    assert report.run_id == "ghost"


def test_waste_premium_misuse_needs_declared_risk(tmp_path: Path) -> None:
    _usage(tmp_path, "run-1")
    report = detect_waste(tmp_path, "run-1")
    assert not any(f.kind == "premium_model_misuse" for f in report.findings)
    assert any("premium_model_misuse" in item for item in report.unresolved)


def test_waste_bad_policy_refuses(tmp_path: Path) -> None:
    from apiforge.agentops.waste import _load_policy

    bad = tmp_path / "bad.yaml"
    bad.write_text("not: a mapping\n", encoding="utf-8")
    with pytest.raises(ContractError, match="AF-AGENTOPS-WASTE-POLICY"):
        _load_policy(bad)
    missing = tmp_path / "missing.yaml"
    with pytest.raises(ContractError, match="AF-AGENTOPS-WASTE-POLICY"):
        _load_policy(missing)


def test_waste_findings_sorted_and_labeled(tmp_path: Path) -> None:
    for verb, refs in (
        ("context capsule", (_ref("a"), _ref("a"))),
        ("context expand", (_ref("a"),)),
        ("context expand", (_ref("a"),)),
    ):
        run_ledger.append(tmp_path, _row("run-1", verb, source="knowledge", refs=refs))
    report = detect_waste(tmp_path, "run-1")
    assert all(f.evidence in ("observed", "estimated", "hypothesis") for f in report.findings)
    kinds = [f.kind for f in report.findings]
    assert kinds == sorted(kinds)
