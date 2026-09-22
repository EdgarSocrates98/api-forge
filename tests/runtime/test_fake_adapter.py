import asyncio

from apiforge.runtime.adapters import AgentRequest, FakeModelAdapter


def test_fake_adapter_is_deterministic() -> None:
    adapter = FakeModelAdapter()
    request = AgentRequest(
        invocation_id="i", agent="a", capability="c", prompt="p", output_contract="AgentArtifact/v1"
    )
    first = asyncio.run(adapter.invoke(request))
    second = asyncio.run(adapter.invoke(request))
    assert first.output == second.output
    assert len(adapter.calls) == 2
