import json
import shutil
from pathlib import Path

import pytest
import yaml

from apiforge.context.gateway.errors import GatewayError
from apiforge.evals.economy import (
    BASELINE_FILE,
    load_corpus,
    record_baseline,
    run_economy,
    summarize,
)

REPO = Path(__file__).resolve().parents[2]
CORPUS = REPO / "evals" / "corpus" / "economy"


def _row(case_id: str, reduction: float, capsule_recall: float = 1.0) -> dict[str, object]:
    return {
        "case_id": case_id,
        "reduction": reduction,
        "baseline_recall": 1.0,
        "capsule_recall": capsule_recall,
        "deterministic": True,
    }


def test_corpus_has_twelve_unique_cases_with_ground_truth() -> None:
    cases = load_corpus(CORPUS)
    assert len(cases) == 12
    assert all(case.required_refs for case in cases)
    recorded = json.loads((CORPUS / BASELINE_FILE).read_text(encoding="utf-8"))["cases"]
    assert set(recorded) == {case.case_id for case in cases}


def test_quality_floor_is_never_traded_for_bytes() -> None:
    result = summarize([_row("a", 0.9, capsule_recall=0.5), _row("b", 0.9)], 0.4)
    assert result["passed"] is False
    assert result["gates"]["quality_floor"] is False
    assert result["quality_failures"] == ["a"]


def test_median_reduction_gate() -> None:
    assert summarize([_row("a", 0.3), _row("b", 0.35), _row("c", 0.9)], 0.4)["passed"] is False
    assert summarize([_row("a", 0.3), _row("b", 0.45), _row("c", 0.9)], 0.4)["passed"] is True


def _single_case_corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    shutil.copyfile(CORPUS / "fastapi-payments-create.yaml", corpus / "case.yaml")
    return corpus


def test_missing_baseline_is_refused(tmp_path: Path) -> None:
    with pytest.raises(GatewayError) as error:
        run_economy(_single_case_corpus(tmp_path), REPO)
    assert error.value.code == "AF-EVALS-ECONOMY-BASELINE-MISSING"


def test_stale_baseline_is_refused(tmp_path: Path) -> None:
    corpus = _single_case_corpus(tmp_path)
    record_baseline(corpus, REPO)
    path = corpus / BASELINE_FILE
    document = json.loads(path.read_text(encoding="utf-8"))
    document["cases"]["fastapi-payments-create"]["fixture_sha256"] = "0" * 64
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(GatewayError) as error:
        run_economy(corpus, REPO)
    assert error.value.code == "AF-EVALS-ECONOMY-BASELINE-STALE"


def test_single_case_meets_quality_and_reduction(tmp_path: Path) -> None:
    corpus = _single_case_corpus(tmp_path)
    record_baseline(corpus, REPO)
    result = run_economy(corpus, REPO)
    row = result["rows"][0]
    assert row["capsule_recall"] == row["baseline_recall"] == 1.0
    assert row["deterministic"] is True
    assert row["effective_bytes"] < row["baseline_bytes"]
    assert result["tokens"] == "unresolved"


def test_case_yaml_declares_kinds_from_the_closed_vocabulary() -> None:
    kinds = {"contract", "schema", "code", "test", "policy", "knowledge"}
    for path in CORPUS.glob("*.yaml"):
        for ref in yaml.safe_load(path.read_text(encoding="utf-8"))["required_refs"]:
            assert ref["kind"] in kinds
