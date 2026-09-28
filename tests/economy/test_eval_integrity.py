"""Eval integrity: certification gates must fail on the bugs they certify against."""

import json
from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy import CostVector, RunLedgerEntry
from apiforge.economy import run_ledger
from apiforge.evals.agentic_quality import run_agentic_quality


def _case(corpus: Path, case_id: str, truth: str, answer: str) -> None:
    corpus.mkdir(parents=True, exist_ok=True)
    (corpus / f"{case_id}.yaml").write_text(
        f"id: {case_id}\noutcome: evaluate {case_id}\nrisk: read_only\n"
        f"ground_truth: {truth}\ndefault_verdict: {answer}\n",
        encoding="utf-8",
    )


def test_equally_wrong_profiles_fail_the_quality_gate(tmp_path: Path) -> None:
    _case(tmp_path / "corpus", "all-wrong", "breaking", "compatible")
    report = run_agentic_quality(tmp_path / "corpus")
    assert report["accuracy"] == {"economy": 0.0, "balanced": 0.0, "deep": 0.0}
    assert report["gates"]["economy_not_below_deep"] is True  # the old gate alone passed
    assert report["gates"]["deep_quality_floor"] is False
    assert report["passed"] is False


def test_baseline_regression_fails_and_equal_passes(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    _case(corpus, "right", "breaking", "breaking")
    _case(corpus, "wrong", "breaking", "compatible")
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "schema": "apiforge/agentic-quality-eval/v1",
                "accuracy": {"economy": 1.0, "balanced": 1.0, "deep": 1.0},
            }
        ),
        encoding="utf-8",
    )
    regressed = run_agentic_quality(corpus, min_accuracy=0.0, baseline=baseline)
    assert regressed["gates"]["economy_not_below_baseline"] is False
    assert regressed["passed"] is False
    assert regressed["baseline_sha256"]
    baseline.write_text(json.dumps(regressed), encoding="utf-8")
    same = run_agentic_quality(corpus, min_accuracy=0.0, baseline=baseline)
    assert same["gates"]["economy_not_below_baseline"] is True


def test_invalid_baseline_and_floor_are_refused(tmp_path: Path) -> None:
    _case(tmp_path / "corpus", "right", "breaking", "breaking")
    bad = tmp_path / "bad.json"
    bad.write_text("{}", encoding="utf-8")
    with pytest.raises(ContractError) as err:
        run_agentic_quality(tmp_path / "corpus", baseline=bad)
    assert err.value.code == "AF-EVALS-BASELINE-INVALID"
    with pytest.raises(ContractError) as err:
        run_agentic_quality(tmp_path / "corpus", min_accuracy=1.5)
    assert err.value.code == "AF-EVALS-INPUT-INVALID"


def _row(run: str, verb: str, tokens: int | None) -> RunLedgerEntry:
    return RunLedgerEntry(
        run_id=run,
        verb=verb,
        source="envelope",
        cost=CostVector(context_bytes=1, observed_tokens=tokens),
    )


def test_deterministic_rows_do_not_count_as_unmeasured_calls(tmp_path: Path) -> None:
    run_ledger.append(tmp_path, _row("r", "context capsule", None))
    run_ledger.append(tmp_path, _row("r", "provider call", 1000))
    run_ledger.append(tmp_path, _row("r", "runtime role:specialist", 500))
    stats = run_ledger.stats(tmp_path)
    assert stats["token_coverage"] == {"status": "complete", "observed_rows": 2, "eligible_rows": 2}
    assert stats["observed_tokens"] == 1500


def test_only_deterministic_rows_leave_tokens_unresolved(tmp_path: Path) -> None:
    run_ledger.append(tmp_path, _row("r", "context capsule", None))
    stats = run_ledger.stats(tmp_path)
    assert stats["token_coverage"]["status"] == "unresolved"
    assert stats["tokens_unresolved"] is True


def test_persist_failures_are_scoped_by_run(tmp_path: Path) -> None:
    (tmp_path / ".apiforge" / "economy.jsonl").mkdir(parents=True)
    assert (
        run_ledger.append(tmp_path, _row("run-A", "runtime role:x", None), auditable=True) is False
    )
    stats_b = run_ledger.stats(tmp_path, run_id="run-B")
    assert stats_b["persist_failures_for_run"] == 0
    assert stats_b["persist_failures_global"] == 1
    assert run_ledger.PERSIST_FAILURE not in stats_b["unresolved"]
    stats_a = run_ledger.stats(tmp_path, run_id="run-A")
    assert stats_a["persist_failures_for_run"] == 1
    assert run_ledger.PERSIST_FAILURE in stats_a["unresolved"]


REPO = Path(__file__).resolve().parents[2]
HARDENING = REPO / "evals" / "corpus" / "economy-hardening"


def test_hardening_eval_runs_production_code(monkeypatch: pytest.MonkeyPatch) -> None:
    from types import SimpleNamespace

    from apiforge.evals.hardening import run_hardening
    from apiforge.runtime import role_context

    assert run_hardening(HARDENING, REPO)["passed"] is True

    def over_budget(*args: object, **kwargs: object) -> object:
        return SimpleNamespace(capsule_id="c", total_bytes=10**9)

    monkeypatch.setattr(role_context, "plan_roles", over_budget)
    mutated = run_hardening(HARDENING, REPO)
    assert mutated["gates"]["budget"] is False
    assert mutated["passed"] is False


def test_changed_path_outside_the_root_is_never_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from apiforge.context import delta
    from tests.context.gateway_support import analyzed_root

    root = analyzed_root(tmp_path)
    (root.parent / "secret.py").write_text("TOKEN = 'x'\n", encoding="utf-8")
    opened: list[Path] = []
    original = delta._mentions

    def spy(path: Path, symbols: object) -> bool:
        opened.append(Path(path))
        return original(path, symbols)  # type: ignore[arg-type]

    monkeypatch.setattr(delta, "_mentions", spy)
    result = delta.build_delta(root, changed=["../secret.py", str(root.parent / "secret.py")])
    assert result.status == "unresolved"
    assert all(item.startswith("AF-PATH-OUTSIDE-ROOT") for item in result.unresolved)
    assert not any(path.name == "secret.py" for path in opened)
    assert result.changed_files == ()


def test_case_dir_outside_the_root_is_refused(tmp_path: Path) -> None:
    from apiforge.context.delta import build_delta
    from apiforge.context.gateway.capsule import build_capsule
    from apiforge.evidence.resolve import resolve
    from tests.context.gateway_support import analyzed_root

    root = analyzed_root(tmp_path)
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    calls = (
        lambda: build_delta(root, changed=["openapi.yaml"], case_dir=outside),
        lambda: build_capsule(root, "POST /payments", case_dir=outside),
        lambda: resolve(root, "evidence://operation/POST /payments", case_dir=outside),
    )
    for call in calls:
        with pytest.raises(ContractError) as err:
            call()
        assert err.value.code == "AF-PATH-OUTSIDE-ROOT"
        assert err.value.field == "case_dir"  # type: ignore[attr-defined]
