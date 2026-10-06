from pathlib import Path

import yaml

from apiforge.evals.runtime_gate import run_runtime_gate
from apiforge.evals.suite import EvalCase, evaluate_case
from apiforge.runtime.feedback import update_scorecard
from apiforge.runtime.registry import load_profiles


def test_runtime_eval_cases_declare_refusal_and_evidence_expectations() -> None:
    cases = yaml.safe_load(Path("tests/evals/cases/runtime_cases.yaml").read_text(encoding="utf-8"))
    assert {case["expected"] for case in cases["cases"]} >= {"REVIEW", "BLOCKED"}


def test_kernel_evolution_gate_requires_all_quality_kinds() -> None:
    path = Path("tests/evals/cases/kernel_evolution.yaml")
    observations = {
        "kernel-control-replay": {
            "observed": "REVIEW",
            "evidence": ["control-replay"],
            "axes": {"status": True, "evidence": True},
            "holdout_payload": {"run": "control"},
        },
        "kernel-lease-holdout": {
            "observed": "REVIEW",
            "evidence": ["lease-recovery"],
            "axes": {"status": True, "evidence": True},
            "holdout_payload": {"run": "lease"},
        },
        "kernel-rollback-mutation": {
            "observed": "BLOCKED",
            "evidence": ["rollback-conflict"],
            "axes": {"status": True, "safety": True},
            "holdout_payload": {"run": "rollback"},
        },
    }
    result = run_runtime_gate(path, observations)
    assert result["status"] == "PASS"
    assert result["quality_gate"] is True


def test_kernel_evolution_gate_blocks_missing_mutation_case() -> None:
    result = run_runtime_gate(
        Path("tests/evals/cases/kernel_evolution.yaml"),
        {"kernel-control-replay": {"observed": "REVIEW", "evidence": ["control-replay"]}},
    )
    assert result["status"] == "BLOCKED"
    assert "kernel-lease-holdout" in result["missing_cases"]
    assert "mutation" in result["missing_kinds"]


def test_experience_interoperability_gate_covers_all_required_quality_kinds() -> None:
    path = Path("tests/evals/cases/experience_interoperability.yaml")
    observations = {
        "experience-tui-parity": {
            "observed": "PASS",
            "evidence": ["projection-parity"],
            "axes": {"parity": True},
            "holdout_payload": {"status": "REVIEW"},
        },
        "experience-knowledge-freshness": {
            "observed": "PASS",
            "evidence": ["freshness-receipt"],
            "axes": {"freshness": True},
            "holdout_payload": {"source_hash": "different"},
        },
        "experience-host-intersection": {
            "observed": "PASS",
            "evidence": ["host-declarations"],
            "axes": {"limitations": True},
            "holdout_payload": {"copilot": "unsupported"},
        },
        "experience-python-observation": {
            "observed": "PASS",
            "evidence": ["runtime-receipt"],
            "axes": {"observed-only": True},
            "holdout_payload": {"version": "3.13"},
        },
        "experience-adaptive-debate": {
            "observed": "PASS",
            "evidence": ["replay-id", "dissent"],
            "axes": {"bounded": True},
            "holdout_payload": {"budget": 2},
        },
    }
    result = run_runtime_gate(path, observations)
    assert result["status"] == "PASS"
    assert result["quality_gate"] is True


def test_routing_feedback_does_not_promote_incomplete_gate(tmp_path: Path) -> None:
    result = evaluate_case(
        EvalCase(
            case_id="routing-missing-holdout",
            domain="runtime",
            input_ref="fixture",
            expected="PASS",
            required_evidence=("routing",),
            mutation="none",
            quality_axes=(),
            kind="golden",
        ),
        observed="PASS",
        evidence=("routing",),
    )
    feedback, scorecard = update_scorecard(
        tmp_path,
        load_profiles()["api-contract-review"],
        (result,),
        gate={
            "status": "BLOCKED",
            "missing_kinds": ("holdout", "mutation"),
        },
    )
    assert feedback.status == "blocked"
    assert scorecard is not None
    assert scorecard.quality_promoted is False
