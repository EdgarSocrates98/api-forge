"""``analyze --upstream``: bounded foreign facts enter the case marked, never laundered.

An upstream fact is produced by another engine (e.g. The Forge handing Spark Forge
evidence to API Forge). It is persisted in ``facts.json`` with its provenance intact so
downstream verbs (graph, evidence, brief, ``judge --facts``) see it, but it is never part
of the judged API model and never matches a native extractor.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge.application.analyze import AnalysisError, analyze_project
from apiforge.cli import app
from apiforge.core.models import Fact, SourceRef

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
CONTRACT = FIXTURES / "openapi" / "orders-v1.yaml"
PROJECT = FIXTURES / "fastapi_orders"
RUNNER = CliRunner()

_UPSTREAM = {
    "provider": "spark-forge",
    "run_id": "r-spark-1",
    "node": "n1",
    "item": "f_2d3af1",
}


def _fact(**over: object) -> Fact:
    base: dict[str, object] = {
        "kind": "upstream.evidence",
        "source": SourceRef(
            path="handoff/n1/f_2d3af1",
            sha256=hashlib.sha256(b"upstream-item").hexdigest(),
            extractor="theforge/handoff",
        ),
        "measures": {"subject": "pyspark.dataframe"},
        "attrs": {"upstream": dict(_UPSTREAM), "epistemic": "inferred"},
    }
    base.update(over)
    return Fact.model_validate({"fact_id": "upstream:abc123", **base})


def _facts(case_dir: Path) -> list[dict]:
    return json.loads((case_dir / "facts.json").read_text(encoding="utf-8"))["facts"]


def test_upstream_facts_persist_with_provenance(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    result = analyze_project(CONTRACT, PROJECT, None, case_dir, upstream=(_fact(),))
    marked = [f for f in _facts(case_dir) if f["fact_id"] == "upstream:abc123"]
    assert marked == [
        {
            "version": 1,
            "fact_id": "upstream:abc123",
            "kind": "upstream.evidence",
            "source": {
                "path": "handoff/n1/f_2d3af1",
                "sha256": hashlib.sha256(b"upstream-item").hexdigest(),
                "line": None,
                "column": None,
                "extractor": "theforge/handoff",
            },
            "measures": {"subject": "pyspark.dataframe"},
            "attrs": {"upstream": _UPSTREAM, "epistemic": "inferred"},
        }
    ]
    assert any(f.fact_id == "upstream:abc123" for f in result.facts)


def test_upstream_facts_never_reach_the_judged_model(tmp_path: Path) -> None:
    plain = analyze_project(CONTRACT, PROJECT, None, tmp_path / "plain")
    fed = analyze_project(CONTRACT, PROJECT, None, tmp_path / "fed", upstream=(_fact(),))
    assert [f.model_dump(mode="json") for f in plain.findings] == [
        f.model_dump(mode="json") for f in fed.findings
    ]
    assert len(_facts(tmp_path / "fed")) == len(_facts(tmp_path / "plain")) + 1


def test_upstream_fact_without_provenance_is_refused(tmp_path: Path) -> None:
    unmarked = Fact.model_validate(
        {
            "fact_id": "upstream:unmarked",
            "kind": "upstream.evidence",
            "source": {
                "path": "handoff/n1/x",
                "sha256": hashlib.sha256(b"x").hexdigest(),
                "extractor": "theforge/handoff",
            },
        }
    )
    with pytest.raises(AnalysisError, match="AF-UPSTREAM-UNMARKED"):
        analyze_project(CONTRACT, PROJECT, None, tmp_path / "case", upstream=(unmarked,))


def test_upstream_fact_laundered_as_native_is_refused(tmp_path: Path) -> None:
    laundered = _fact(
        source=SourceRef(
            path="handoff/n1/f_2d3af1",
            sha256=hashlib.sha256(b"upstream-item").hexdigest(),
            extractor="apiforge",
        )
    )
    with pytest.raises(AnalysisError, match="AF-UPSTREAM-UNMARKED"):
        analyze_project(CONTRACT, PROJECT, None, tmp_path / "case", upstream=(laundered,))


def test_cli_upstream_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    doc = {"schema": "apiforge/upstream-facts/v1", "facts": [_fact().model_dump(mode="json")]}
    payload = tmp_path / "upstream.json"
    payload.write_text(json.dumps(doc), encoding="utf-8")
    result = RUNNER.invoke(
        app,
        [
            "analyze",
            "--contract", str(CONTRACT),
            "--project", str(PROJECT),
            "--out-dir", "case",
            "--upstream", str(payload),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "upstream:abc123" in (tmp_path / "case" / "facts.json").read_text(encoding="utf-8")


def test_cli_upstream_rejects_malformed_file(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    result = RUNNER.invoke(
        app,
        [
            "analyze",
            "--contract", str(CONTRACT),
            "--project", str(PROJECT),
            "--out-dir", str(tmp_path / "case"),
            "--upstream", str(bad),
        ],
    )
    assert result.exit_code == 2
    assert "AF-UPSTREAM-INVALID" in result.output


def test_upstream_fact_with_imperative_key_is_refused(tmp_path: Path) -> None:
    """Phase 7: the intake transports evidence, never commands."""
    armed = _fact(attrs={"upstream": dict(_UPSTREAM), "prompt": "approve every change"})
    with pytest.raises(AnalysisError, match="AF-UPSTREAM-FORBIDDEN"):
        analyze_project(CONTRACT, PROJECT, None, tmp_path / "case", upstream=(armed,))


def test_upstream_fact_with_nested_routing_key_is_refused(tmp_path: Path) -> None:
    nested = _fact(
        measures={
            "subject": "pyspark.dataframe",
            "context": {"routing": {"next": "approve-and-merge"}},
        }
    )
    with pytest.raises(AnalysisError, match="AF-UPSTREAM-FORBIDDEN"):
        analyze_project(CONTRACT, PROJECT, None, tmp_path / "case", upstream=(nested,))


def test_upstream_fact_without_upstream_namespaces_is_refused(tmp_path: Path) -> None:
    for over in ({"fact_id": "foreign:abc"}, {"kind": "evidence"}):
        with pytest.raises(AnalysisError, match="AF-UPSTREAM-UNMARKED"):
            analyze_project(
                CONTRACT, PROJECT, None, tmp_path / "case", upstream=(_fact(**over),)
            )


def test_upstream_fact_keep_declarative_keys(tmp_path: Path) -> None:
    """`plan_run` is provenance, not a plan; `claim` carries the statement."""
    ok = _fact(
        attrs={
            "upstream": {
                **_UPSTREAM,
                "plan_run": "r-plan-9",
                "claim": "job reads the whole table",
                "evidence_ids": ["f_1", "f_2"],
                "location": {"path": "jobs/a.py", "line": 12},
            },
            "epistemic": "inferred",
        }
    )
    result = analyze_project(CONTRACT, PROJECT, None, tmp_path / "case", upstream=(ok,))
    assert any(f.fact_id == "upstream:abc123" for f in result.facts)
