import pytest

from apiforge.contracts.base import ContractError
from apiforge.runtime.policy import load_policy, validate_tool


def test_external_mutation_and_shell_are_not_allowlisted() -> None:
    policy = load_policy("local-ci-safe")
    assert policy.allow_external_mutation is False
    with pytest.raises(ContractError):
        validate_tool(policy, "shell:curl", external_mutation=False)
