"""Hardening 3: baselines must measure the same benchmark; the eligibility policy fails closed."""

import json
from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy import CostVector, RunLedgerEntry
from apiforge.economy import run_ledger
from apiforge.economy.run_ledger import eligible_prefixes
from apiforge.evals.agentic_quality import run_agentic_quality


def _case(corpus: Path, case_id: str, truth: str = "breaking", answer: str = "breaking") -> None:
    corpus.mkdir(parents=True, exist_ok=True)
    (corpus / f"{case_id}.yaml").write_text(
        f"id: {case_id}\noutcome: evaluate {case_id}\nrisk: read_only\n"
        f"ground_truth: {truth}\ndefault_verdict: {answer}\n",
        encoding="utf-8",
    )


@pytest.fixture
def two_corpora(tmp_path: Path) -> tuple[Path, Path, Path]:
    first, second = tmp_path / "a", tmp_path / "b"
    _case(first, "case-1")
    _case(second, "case-1")
    _case(second, "case-2")
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps(run_agentic_quality(first)), encoding="utf-8")
    return first, second, baseline


def test_report_carries_a_stable_benchmark_identity(tmp_path: Path) -> None:
    _case(tmp_path / "c", "case-1")
    first = run_agentic_quality(tmp_path / "c")["benchmark_identity"]
    assert first == run_agentic_quality(tmp_path / "c")["benchmark_identity"]
    assert first["case_count"] == 1 and first["profiles"] == ["economy", "balanced", "deep"]
    (tmp_path / "c" / "case-1.yaml").write_text(
        "id: case-1\noutcome: changed\nrisk: read_only\n"
        "ground_truth: breaking\ndefault_verdict: breaking\n",
        encoding="utf-8",
    )
    assert (
        run_agentic_quality(tmp_path / "c")["benchmark_identity"]["corpus_sha256"]
        != (first["corpus_sha256"])
    )


def test_same_corpus_baseline_is_accepted(two_corpora: tuple[Path, Path, Path]) -> None:
    first, _, baseline = two_corpora
    report = run_agentic_quality(first, baseline=baseline)
    assert report["baseline_scope"] == "same_corpus"
    assert report["gates"]["economy_not_below_baseline"] is True


def test_baseline_of_another_corpus_is_refused(two_corpora: tuple[Path, Path, Path]) -> None:
    _, second, baseline = two_corpora
    with pytest.raises(ContractError) as err:
        run_agentic_quality(second, baseline=baseline)
    assert err.value.code == "AF-EVALS-BASELINE-MISMATCH"
    assert err.value.field == "baseline"  # type: ignore[attr-defined]


def test_cross_corpus_baseline_needs_the_flag_and_is_recorded(
    two_corpora: tuple[Path, Path, Path],
) -> None:
    _, second, baseline = two_corpora
    report = run_agentic_quality(second, baseline=baseline, allow_cross_corpus_baseline=True)
    assert report["baseline_scope"] == "cross_corpus"
    assert "economy_not_below_baseline_cross_corpus" in report["gates"]
    assert "economy_not_below_baseline" not in report["gates"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda data: data.pop("benchmark_identity"),
        lambda data: data["accuracy"].pop("deep"),
        lambda data: data["accuracy"].__setitem__("economy", 1.5),
    ],
    ids=["legacy-no-identity", "missing-profile", "out-of-range"],
)
def test_malformed_baselines_are_invalid(two_corpora: tuple[Path, Path, Path], mutate) -> None:
    first, _, baseline = two_corpora
    data = json.loads(baseline.read_text(encoding="utf-8"))
    mutate(data)
    baseline.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ContractError) as err:
        run_agentic_quality(first, baseline=baseline)
    assert err.value.code == "AF-EVALS-BASELINE-INVALID"


@pytest.mark.parametrize(
    "rule",
    [
        "schema: apiforge/token-eligibility/v1\nverb_prefixes: []\n",
        'schema: apiforge/token-eligibility/v1\nverb_prefixes: [""]\n',
        'schema: apiforge/token-eligibility/v1\nverb_prefixes: ["  "]\n',
        'schema: apiforge/token-eligibility/v1\nverb_prefixes: ["provider", "provider"]\n',
        'schema: something-else\nverb_prefixes: ["provider"]\n',
    ],
    ids=["empty", "blank", "whitespace", "duplicate", "wrong-schema"],
)
def test_eligibility_policy_fails_closed(tmp_path: Path, rule: str) -> None:
    path = tmp_path / "token_eligibility.yaml"
    path.write_text(rule, encoding="utf-8")
    with pytest.raises(ContractError) as err:
        eligible_prefixes(str(path))
    assert err.value.code == "AF-ECONOMY-TOKEN-RULE-INVALID"


def test_unmeasured_provider_keeps_coverage_partial(tmp_path: Path) -> None:
    for tokens in (1000, None):
        run_ledger.append(
            tmp_path,
            RunLedgerEntry(
                run_id="r",
                verb="provider call",
                source="envelope",
                cost=CostVector(context_bytes=1, observed_tokens=tokens),
            ),
        )
    assert run_ledger.stats(tmp_path)["token_coverage"]["status"] == "partial"
