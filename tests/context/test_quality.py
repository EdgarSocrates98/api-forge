"""Context Quality Engine: metric catalog, unresolved honesty and ledger derivation."""

from __future__ import annotations

import hashlib

import pytest

from apiforge.context.quality import evaluate, metric_map, role_telemetry
from apiforge.contracts.context import ContextRef
from apiforge.contracts.context_quality import (
    METRIC_KINDS,
    ContextQualityReport,
    ContextUseRecord,
    RoleContextPolicy,
)


def _uri(seed: str) -> str:
    return f"ctx://sha256/{hashlib.sha256(seed.encode()).hexdigest()}"


def _ref(
    seed: str,
    *,
    kind: str = "code",
    size: int = 100,
    parity: bool | None = None,
    origin: str = "code",
    source: str | None = None,
) -> ContextRef:
    return ContextRef(
        uri=_uri(seed),
        kind=kind,  # type: ignore[arg-type]
        label=seed,
        source=source or f"{seed}.py",
        size_bytes=size,
        provenance="test",
        origin=origin,  # type: ignore[arg-type]
        parity=parity,
    )


def _use(
    run: str,
    ref: ContextRef,
    action: str,
    *,
    role: str | None = None,
    bytes_: int = 0,
    tokens: int | None = None,
    seq: int = 0,
) -> ContextUseRecord:
    return ContextUseRecord(
        use_id=f"{run}:{seq}",
        run_id=run,
        ref_uri=ref.uri,
        action=action,  # type: ignore[arg-type]
        role=role,
        bytes=bytes_,
        tokens=tokens,
    )


def test_report_emits_every_metric_kind() -> None:
    refs = (_ref("a", kind="contract", origin="contract", parity=True), _ref("b"))
    uses = (_use("r", refs[0], "expanded", role="specialist"),)
    report = evaluate(refs, uses, run_id="r", required_uris=[refs[0].uri])
    assert set(metric_map(report.metrics)) == set(METRIC_KINDS)


def test_metrics_are_measured_not_invented() -> None:
    refs = (
        _ref("contract", kind="contract", origin="contract", size=100, parity=True),
        _ref("code", kind="code", size=200, parity=True),
        _ref("test", kind="test", size=50, parity=False),
    )
    uses = (
        _use("r", refs[0], "expanded", role="specialist", bytes_=100, tokens=10),
        _use("r", refs[0], "cited", role="reviewer"),
        _use("r", refs[1], "expanded", role="specialist", bytes_=200, tokens=30),
    )
    missing_required = _uri("not-in-capsule")
    report = evaluate(
        refs,
        uses,
        run_id="r",
        required_uris=[refs[0].uri, refs[2].uri, missing_required],
        cache_hits=2,
        cache_lookups=4,
    )
    metrics = metric_map(report.metrics)
    assert metrics["context_precision"].value == pytest.approx(2 / 3, abs=1e-3)
    assert metrics["context_recall"].value == pytest.approx(2 / 3, abs=1e-3)
    assert metrics["evidence_recall"].value == pytest.approx(0.5, abs=1e-3)
    assert metrics["context_density"].value == pytest.approx(300 / 350, abs=1e-3)
    assert metrics["irrelevant_context_ratio"].value == pytest.approx(1 / 3, abs=1e-3)
    assert metrics["stale_context_ratio"].value == pytest.approx(1 / 3, abs=1e-3)
    assert metrics["context_reuse_rate"].value == pytest.approx(0.5, abs=1e-3)
    assert metrics["cache_hit_rate"].value == pytest.approx(0.5)
    assert metrics["evidence_per_token"].value == pytest.approx(1 / 40, abs=1e-3)
    assert metrics["useful_facts_per_1k_tokens"].value == pytest.approx(50.0, abs=0.1)
    assert report.status == "ready"


def test_unresolved_metrics_carry_no_value() -> None:
    report = evaluate((), (), run_id="empty")
    metrics = metric_map(report.metrics)
    assert metrics["context_precision"].basis == "unresolved"
    assert metrics["context_precision"].value is None
    assert report.status == "unresolved"
    assert report.unresolved


def test_duplicate_context_counts_shadowed_spans() -> None:
    dup_a = _ref("dup-a", source="src/x.py")
    dup_b = ContextRef(
        uri=_uri("dup-b"),
        kind="code",
        label="dup-b",
        source="src/x.py",
        size_bytes=80,
        provenance="test",
        origin="code",
    )
    report = evaluate((dup_a, dup_b), (), run_id="r")
    metrics = metric_map(report.metrics)
    assert metrics["duplicate_context_ratio"].value == pytest.approx(80 / 180, abs=1e-3)


def test_role_telemetry_counts_per_role() -> None:
    refs = (_ref("a", kind="contract", origin="contract"), _ref("b"))
    uses = (
        _use("r", refs[0], "assigned", role="specialist", seq=1),
        _use("r", refs[1], "assigned", role="specialist", seq=2),
        _use("r", refs[0], "expanded", role="specialist", seq=3, tokens=5),
    )
    rows = {row.role: row for row in role_telemetry(refs, uses, run_id="r")}
    row = rows["specialist"]
    assert row.refs_assigned == 2
    assert row.refs_expanded == 1
    assert row.unused_refs == 1
    assert row.evidence_refs == 1
    assert row.tokens == 5


def test_report_is_frozen_and_closed() -> None:
    report = evaluate((), (), run_id="r")
    assert isinstance(report, ContextQualityReport)
    with pytest.raises(ValueError):
        report.model_copy(update={"unknown_field": 1}).model_validate(
            {**report.model_dump(), "unknown_field": 1}
        )


def test_metric_contract_rejects_value_on_unresolved() -> None:
    from apiforge.contracts.context_quality import ContextQualityMetric

    with pytest.raises(ValueError):
        ContextQualityMetric(name="context_precision", basis="unresolved", value=0.5)


def test_policy_contract_rejects_overlapping_kinds() -> None:
    with pytest.raises(ValueError):
        RoleContextPolicy(role="reviewer", required_kinds=("policy",), denied_kinds=("policy",))
