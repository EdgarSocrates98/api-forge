from pathlib import Path

from apiforge.evals.context_quality import run_context_quality


def test_context_quality_counterfactual_ablation_is_reported() -> None:
    root = Path(__file__).resolve().parents[2]
    report = run_context_quality(root / "evals" / "corpus" / "context-quality")
    assert report["passed"]
    noisy = next(item for item in report["cases"] if item["id"] == "noisy-capsule")
    assert noisy["counterfactual"]["decision_stable"] is False
    assert len(noisy["counterfactual"]["ablations"]) == 4
