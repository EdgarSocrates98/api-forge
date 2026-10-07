from pathlib import Path

from apiforge.evals.economy_routing import load_cases, run_economy_routing, summarize

CORPUS = Path(__file__).resolve().parents[2] / "evals" / "corpus" / "economy-routing"


def _row(**updates) -> dict:
    row = {
        "case_id": "c",
        "shape": "small",
        "profile": "economy",
        "effective": "economy",
        "expected_effective": "economy",
        "minimum_roles": ["reviewer"],
        "expected_minimum_roles": ["reviewer"],
        "baseline_roles": ["reviewer"],
        "economy_roles": ["reviewer"],
        "baseline_fanout": 5,
        "economy_fanout": 0,
        "baseline_calls": 6,
        "economy_calls": 2,
    }
    row.update(updates)
    return row


def test_corpus_has_fifteen_cases_across_five_shapes() -> None:
    cases = load_cases(CORPUS)
    assert len(cases) == 15
    assert {case.shape for case in cases} == {
        "small",
        "moderate",
        "complex",
        "sensitive",
        "critical",
    }
    assert all(case.expected_effective == "deep" for case in cases if case.shape == "critical")


def test_dropping_a_risk_role_fails_the_invariant() -> None:
    result = summarize([_row(economy_roles=[])])
    assert result["passed"] is False
    assert result["role_violations"] == ["c"]


def test_critical_must_resolve_deep() -> None:
    result = summarize(
        [_row(shape="critical", effective="balanced", expected_effective="balanced")]
    )
    assert result["gates"]["critical_is_deep"] is False


def test_economy_must_be_cheaper_for_low_risk() -> None:
    result = summarize([_row(economy_fanout=5)])
    assert result["gates"]["economy_cheaper_low_risk"] is False


def test_real_corpus_passes_all_gates() -> None:
    result = run_economy_routing(CORPUS)
    assert result["passed"] is True, result
    assert result["cases"] == 15
    blocked = [row for row in result["rows"] if row["runtime"] == "review-blocked"]
    assert all(row["shape"] == "critical" and row["economy_calls"] is None for row in blocked)
