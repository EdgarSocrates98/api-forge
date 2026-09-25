from pathlib import Path

from apiforge.evals.runtime_gate import ADVERSARIAL_REQUIRED_KINDS, run_runtime_gate


def _observations() -> dict[str, dict[str, object]]:
    return {
        "scorecard-adaptive-golden": {
            "observed": "PASS",
            "evidence": ["scorecard-assessment", "routing-plan", "shadow-evaluation"],
            "axes": {"champion-selection": True},
        },
        "scorecard-adaptive-holdout": {
            "observed": "PASS",
            "evidence": ["scorecard-assessment", "challenger-bound"],
            "axes": {"anti-starvation": True, "replay": True},
        },
        "scorecard-adaptive-mutation": {
            "observed": "BLOCKED",
            "evidence": ["scorecard-assessment", "freshness-gap"],
            "axes": {"freshness-safety": True},
        },
        "scorecard-adaptive-adversarial": {
            "observed": "PASS",
            "evidence": ["scorecard-assessment", "replay"],
            "axes": {"provenance": True, "determinism": True},
        },
    }


def test_scorecard_adaptive_gate_requires_all_case_kinds() -> None:
    result = run_runtime_gate(
        Path("tests/evals/cases/scorecard_adaptive_routing.yaml"),
        _observations(),
        required_kinds=ADVERSARIAL_REQUIRED_KINDS,
    )

    assert result["status"] == "PASS"
    assert result["quality_gate"] is True


def test_scorecard_adaptive_gate_blocks_missing_adversarial_case() -> None:
    observations = _observations()
    observations.pop("scorecard-adaptive-adversarial")

    result = run_runtime_gate(
        Path("tests/evals/cases/scorecard_adaptive_routing.yaml"),
        observations,
        required_kinds=ADVERSARIAL_REQUIRED_KINDS,
    )

    assert result["status"] == "BLOCKED"
    assert "adversarial" in result["missing_kinds"]
