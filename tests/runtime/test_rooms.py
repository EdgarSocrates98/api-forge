from apiforge.runtime.policy import load_policy, should_open_room


def test_room_is_user_requestable() -> None:
    assert should_open_room(policy=load_policy("local-ci-safe"), risk="read_only", confidence=0.9, unresolved=(), conflicting_facts=False, requested_by_user=True)[0]
