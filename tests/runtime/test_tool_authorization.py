from __future__ import annotations

import asyncio

import pytest

from apiforge.contracts.base import ContractError
from apiforge.runtime.adapters import AgentRequest, FakeModelAdapter
from apiforge.runtime.supervisor import _authorized_invoke


def test_runtime_adapter_crossing_requires_tool_grant() -> None:
    request = AgentRequest(
        invocation_id="inv:test",
        agent="agent:test",
        capability="capability:test",
        prompt="test",
        output_contract="AgentArtifact/v1",
    )
    response = asyncio.run(_authorized_invoke(FakeModelAdapter(), request))
    assert response is not None


def test_runtime_requested_tool_without_profile_refuses() -> None:
    request = AgentRequest(
        invocation_id="inv:test",
        agent="agent:test",
        capability="capability:test",
        prompt="test",
        tool_names=("undeclared-tool",),
        output_contract="AgentArtifact/v1",
    )
    with pytest.raises(ContractError) as error:
        asyncio.run(_authorized_invoke(FakeModelAdapter(), request))
    assert error.value.code == "AF-TOOL-PROFILE-MISSING"
