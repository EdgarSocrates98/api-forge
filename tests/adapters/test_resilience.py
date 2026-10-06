"""Resilience extractor: static signals, summary fact, AF-RES rule firing."""

from pathlib import Path

from apiforge.adapters.resilience import extract_resilience
from apiforge.rules.fact_judge import judge_facts

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "resilience_app"


def _facts():
    return extract_resilience(FIXTURE).facts


def _hits(rule_id: str) -> list:
    return [f for f in judge_facts(_facts()) if f.rule_id == rule_id]


def test_http_call_without_timeout_fires() -> None:
    hits = _hits("AF-PERF-101")
    assert len(hits) == 1
    assert hits[0].evidence, "finding must cite the http_call fact"


def test_timed_out_call_does_not_fire() -> None:
    # writer.py passes timeout=2.0 — only client.py's bare get fires
    kinds = {f.kind for f in _facts() if f.kind == "resilience.http_call"}
    assert kinds == {"resilience.http_call"}
    timeouts = [f.measures["has_timeout"] for f in _facts() if f.kind == "resilience.http_call"]
    assert sorted(timeouts) == [False, True]


def test_retry_without_backoff_and_mutating() -> None:
    # both fixture retries lack backoff; the POST one is mutating
    assert len(_hits("AF-PERF-102")) == 2
    assert len(_hits("AF-PERF-104")) == 1


def test_no_jitter_fires_on_both() -> None:
    assert len(_hits("AF-PERF-103")) == 2


def test_summary_absences_fire() -> None:
    for rule in ("AF-PERF-105", "AF-PERF-107", "AF-PERF-108"):
        assert _hits(rule), rule


def test_unbounded_pool_fires() -> None:
    assert len(_hits("AF-PERF-106")) == 1


def test_diagnostic_names_the_blind_spot() -> None:
    inv = extract_resilience(FIXTURE)
    codes = {d.code for d in inv.diagnostics}
    assert "AF-RES-HEURISTIC" in codes


def test_clean_project_emits_no_findings(tmp_path: Path) -> None:
    (tmp_path / "mod.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    inv = extract_resilience(tmp_path)
    # summary still emitted (scanned files exist) but no call-site facts
    assert {f.kind for f in inv.facts} == {"resilience.summary"}
    assert not judge_facts(inv.facts)


def test_breaker_declared_silences_af_res_005(tmp_path: Path) -> None:
    (tmp_path / "c.py").write_text(
        "from pybreaker import CircuitBreaker\nbreaker = CircuitBreaker()\n",
        encoding="utf-8",
    )
    inv = extract_resilience(tmp_path)
    hits = [f for f in judge_facts(inv.facts) if f.rule_id == "AF-PERF-105"]
    assert not hits
