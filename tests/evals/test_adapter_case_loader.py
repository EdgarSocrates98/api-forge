from __future__ import annotations

from pathlib import Path

from apiforge.evals.suite import load_cases


def test_adapter_eval_cases_preserve_adapter_identity() -> None:
    cases = load_cases(Path("evals/cases/adapter-depth.yaml"))
    assert {case.adapter for case in cases} == {"relational", "streaming"}
    assert all(case.input_ref.startswith("tests/") for case in cases)
