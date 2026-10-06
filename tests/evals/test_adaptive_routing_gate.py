from pathlib import Path

from apiforge.evals.runtime_gate import ADVERSARIAL_REQUIRED_KINDS, run_runtime_gate


def _observations() -> dict[str, dict[str, object]]:
    return {
        "adaptive-routing-golden": {
            "observed": "PASS",
            "evidence": ["routing-plan"],
            "axes": {"deterministic": True},
        },
        "adaptive-routing-holdout": {
            "observed": "PASS",
            "evidence": ["routing-replay"],
            "axes": {"replay": True},
        },
        "adaptive-routing-mutation": {
            "observed": "BLOCKED",
            "evidence": ["refusal"],
            "axes": {"safety": True},
        },
        "adaptive-routing-adversarial": {
            "observed": "BLOCKED",
            "evidence": ["adversarial-refusal"],
            "axes": {"provenance": True},
        },
        "risk-complexity-golden": {
            "observed": "PASS",
            "evidence": ["risk-assessment", "routing-plan", "projection-parity"],
            "axes": {"deterministic": True, "complexity": True},
        },
        "risk-complexity-holdout": {
            "observed": "PASS",
            "evidence": ["risk-assessment", "routing-replay"],
            "axes": {"replay": True, "composition": True},
        },
        "risk-complexity-mutation": {
            "observed": "PASS",
            "evidence": ["risk-assessment", "refusal"],
            "axes": {"safety": True, "complexity": True},
        },
        "risk-complexity-adversarial": {
            "observed": "PASS",
            "evidence": ["risk-assessment", "unresolved", "adversarial-refusal"],
            "axes": {"provenance": True, "evidence": True},
        },
    }


def test_adversarial_kind_is_an_explicit_gate_requirement() -> None:
    result = run_runtime_gate(
        Path("tests/evals/cases/adaptive_routing.yaml"),
        _observations(),
        required_kinds=ADVERSARIAL_REQUIRED_KINDS,
    )

    assert result["status"] == "PASS"
    assert result["quality_gate"] is True


def test_adversarial_kind_cannot_be_omitted() -> None:
    observations = _observations()
    observations.pop("adaptive-routing-adversarial")
    observations.pop("risk-complexity-adversarial")

    result = run_runtime_gate(
        Path("tests/evals/cases/adaptive_routing.yaml"),
        observations,
        required_kinds=ADVERSARIAL_REQUIRED_KINDS,
    )

    assert result["status"] == "BLOCKED"
    assert "adversarial" in result["missing_kinds"]
