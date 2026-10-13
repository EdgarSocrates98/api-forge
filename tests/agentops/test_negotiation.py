from pathlib import Path

from apiforge.agentops.negotiation import (
    default_declarations,
    negotiate,
    negotiate_from_root,
)
from apiforge.contracts.host import HostCapabilityRequest


def test_four_host_negotiation_returns_intersection() -> None:
    result = negotiate(HostCapabilityRequest(capability="mcp"), default_declarations())
    assert result.eligible_hosts == ("claude", "devin", "gpt-codex")
    assert "copilot" in result.excluded_hosts
    assert result.limitations


def test_root_declarations_override_static_fallback(tmp_path: Path) -> None:
    directory = tmp_path / ".apiforge" / "hosts"
    directory.mkdir(parents=True)
    (directory / "copilot.json").write_text(
        '{"host": "copilot", "capabilities": [{"capability": "mcp", '
        '"state": "supported", "evidence": {"level": "observed", "source": "receipt"}}]}',
        encoding="utf-8",
    )
    result = negotiate_from_root(
        tmp_path,
        HostCapabilityRequest(capability="mcp", hosts=("copilot",)),
    )
    assert result.eligible_hosts == ("copilot",)
