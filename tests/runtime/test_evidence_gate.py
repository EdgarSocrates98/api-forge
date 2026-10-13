from apiforge.runtime.evidence_gate import build_evidence_coverage


def test_evidence_gate_preserves_unknown_limitations() -> None:
    coverage = build_evidence_coverage(
        ("task_spec", "rollback"),
        ("task_spec",),
        limitations=("rollback receipt unresolved",),
    )
    assert coverage.state == "partial"
    assert coverage.missing == ("rollback",)
    assert coverage.limitations == ("rollback receipt unresolved",)
