from apiforge.application.experience_projection import project_payload


def test_projection_is_stable_across_surfaces() -> None:
    payload = {"status": "completed", "gaps": ["b", "a"], "run_digest": "sha"}
    snapshot = project_payload("task-1", payload, surface="json")
    assert snapshot.view.status == "DONE"
    assert snapshot.view.gaps == ("a", "b")
    assert snapshot.view.evidence.level == "verified"
    assert snapshot.view.payload == payload


def test_projection_preserves_unknown_states_as_review() -> None:
    snapshot = project_payload("task-1", {"status": "provider-says-ok"})
    assert snapshot.view.status == "REVIEW"
    assert "resume" in snapshot.view.actions


def test_projection_preserves_canonical_routing_assessment_and_gaps() -> None:
    payload = {
        "status": "REVIEW",
        "routing": {
            "evidence": ["task_spec"],
            "unresolved": ["candidate:quality:unresolved"],
            "risk_complexity": {
                "assessment_id": "risk-assessment:test",
                "complexity": "complex",
                "evidence": ["task_spec"],
                "unresolved": ["assessment-gap"],
            },
        },
        "routing_plan": {"evidence": ["routing-plan"], "unresolved": []},
    }

    snapshot = project_payload("task-1", payload)

    assert snapshot.view.payload == payload
    assert snapshot.view.evidence_refs == ("routing-plan", "task_spec")
    assert snapshot.view.gaps == ("assessment-gap", "candidate:quality:unresolved")
