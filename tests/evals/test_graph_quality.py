"""`evals graph-quality` gate (AT-016): the shipped corpus passes; a regressed expectation fails."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.evals.graph_quality import run_graph_quality

CORPUS = Path(__file__).resolve().parents[2] / "evals" / "corpus" / "graph-quality"


def test_shipped_corpus_meets_thresholds() -> None:
    report = run_graph_quality(CORPUS)
    assert report["passed"], report["failures"]
    assert report["bounded_false_positives"] == 0
    assert report["precision"]["python"] == 1.0


def test_regressed_case_fails_and_names_rule(tmp_path: Path) -> None:
    corpus = tmp_path / "graph-quality"
    shutil.copytree(CORPUS, corpus)
    doc = json.loads((corpus / "cases.json").read_text(encoding="utf-8"))
    target = next(case for case in doc["cases"] if case["id"] == "java/g-ok")
    target["expect"] = ["AF-GDB-001"]
    (corpus / "cases.json").write_text(json.dumps(doc), encoding="utf-8")
    report = run_graph_quality(corpus)
    assert report["passed"] is False
    assert {"case": "java/g-ok", "missing": ["AF-GDB-001"], "unexpected": []} in report[
        "mismatches"
    ]
    assert any(failure.startswith("recall[AF-GDB-001/java]") for failure in report["failures"])


def test_missing_corpus_refuses(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="AF-EVALS-INVALID"):
        run_graph_quality(tmp_path)
