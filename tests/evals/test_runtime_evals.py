from pathlib import Path

import yaml


def test_runtime_eval_cases_declare_refusal_and_evidence_expectations() -> None:
    cases = yaml.safe_load(Path("tests/evals/cases/runtime_cases.yaml").read_text(encoding="utf-8"))
    assert {case["expected"] for case in cases["cases"]} >= {"REVIEW", "BLOCKED"}
