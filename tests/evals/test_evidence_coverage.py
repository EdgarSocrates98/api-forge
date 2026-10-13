import pytest

from apiforge.evals.evidence_coverage import calculate_evidence_coverage


@pytest.mark.parametrize(
    ("required", "available", "expected"),
    [
        (("task_spec",), ("task_spec",), "complete"),
        (("task_spec", "receipt"), ("task_spec",), "partial"),
        (("receipt",), (), "missing"),
        ((), ("task_spec",), "unresolved"),
    ],
)
def test_coverage_states_are_deterministic(
    required: tuple[str, ...], available: tuple[str, ...], expected: str
) -> None:
    coverage = calculate_evidence_coverage(required, available)
    assert coverage.state == expected
    assert coverage.missing == tuple(sorted(set(required) - set(available)))


def test_limitations_keep_complete_claims_unresolved() -> None:
    coverage = calculate_evidence_coverage(
        ("task_spec",),
        ("task_spec",),
        limitations=("provider freshness was not observed",),
    )
    assert coverage.state == "unresolved"
    assert coverage.limitations == ("provider freshness was not observed",)
