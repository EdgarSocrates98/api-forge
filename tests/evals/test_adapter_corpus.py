from __future__ import annotations

from pathlib import Path

import yaml


def test_adapter_corpus_references_existing_inputs_and_declares_limits() -> None:
    path = Path("evals/cases/adapter-depth.yaml")
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    cases = document["cases"]
    assert len(cases) == 2
    for case in cases:
        assert Path(case["input"]).exists()
        assert case["required_evidence"]
        assert (
            "no-runtime-inference" in case["quality_axes"] or "no-lag-claim" in case["quality_axes"]
        )
