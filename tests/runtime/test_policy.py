import pytest

from apiforge.contracts.base import ContractError
from apiforge.runtime.policy import load_policy, requires_critic, should_open_room, validate_tool


def test_policy_refuses_mutation_and_triggers_critic() -> None:
    policy = load_policy("local-ci-safe")
    assert requires_critic(policy, "sensitive") is True
    assert should_open_room(
        policy=policy,
        risk="read_only",
        confidence=0.4,
        unresolved=(),
        conflicting_facts=False,
        requested_by_user=False,
    )[0]
    with pytest.raises(ContractError):
        validate_tool(policy, "shell:rm", external_mutation=False)
