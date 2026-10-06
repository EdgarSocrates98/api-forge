from pathlib import Path

from apiforge.evals.suite import evaluate_case, load_cases, mutation_probe


def test_platform_eval_matrix_has_domains_and_mutations() -> None:
    cases = load_cases(Path("evals/cases/platform.yaml"))
    assert len(cases) == 4
    assert {case.domain for case in cases} >= {"contract", "migration", "performance", "agentops"}
    assert all(case.mutation != "none" for case in cases)


def test_eval_blocks_when_evidence_is_missing() -> None:
    case = load_cases(Path("evals/cases/platform.yaml"))[0]
    result = evaluate_case(case, observed="REVIEW", evidence=("api-ir",), axes={})
    assert result.verdict == "BLOCKED"
    assert "contract-diff" in result.missing_evidence


def test_eval_passes_golden_and_holdout_is_digestable() -> None:
    case = load_cases(Path("evals/cases/platform.yaml"))[-1]
    result = evaluate_case(
        case,
        observed="PASS",
        evidence=("source-sha256", "critical-recall"),
        axes={"evidence-recall": True, "byte-savings": True},
        holdout_payload={"critical": "AF-KEEP"},
    )
    assert result.verdict == "PASS"
    assert len(result.holdout_digest or "") == 64
    assert mutation_probe({}, "remove-critical-line")["changed"] is True
