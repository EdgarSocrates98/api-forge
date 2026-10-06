import pytest

from apiforge.agentops.tools import get_tool_adapter, list_tool_adapters


def test_tool_adapter_registry_covers_existing_tools() -> None:
    adapters = list_tool_adapters()
    assert len(adapters) == 12
    k6 = get_tool_adapter("k6")
    assert k6.safety_class == "network_or_credentialed"
    assert k6.evidence_producer == "test.k6.summary"
    assert "local" in k6.modes


def test_unknown_tool_adapter_is_named() -> None:
    with pytest.raises(ValueError, match="AF-TOOL-ADAPTER-UNKNOWN"):
        get_tool_adapter("unknown-tool")
