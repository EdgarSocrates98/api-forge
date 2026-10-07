from __future__ import annotations

from apiforge.contracts.change_control import ChangeBundle, Recommendation


def test_change_bundle_is_versioned_and_read_only() -> None:
    bundle = ChangeBundle(
        repository="example/repo",
        base_sha="0" * 40,
        head_sha="1" * 40,
        origin="replay",
    )
    assert bundle.schema_version == "af-change-bundle/1"
    assert bundle.policy.read_only is True
    assert bundle.policy.mutation_allowed is False


def test_recommendation_has_the_explainability_contract() -> None:
    recommendation = Recommendation(
        recommendation="review",
        verifier="apiforge change-control verify",
        confidence=0.5,
    )
    assert set(recommendation.model_dump()) >= {
        "recommendation",
        "facts",
        "assumptions",
        "alternatives",
        "risks",
        "unresolved",
        "evidence_refs",
        "verifier",
        "confidence",
    }
