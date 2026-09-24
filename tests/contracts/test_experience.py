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
