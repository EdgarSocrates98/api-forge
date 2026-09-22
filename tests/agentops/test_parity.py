from pathlib import Path

from apiforge.agentops.parity import audit_host_parity


def test_host_parity_reports_shared_core_and_host_limits() -> None:
    result = audit_host_parity(Path(__file__).parents[2])

    assert result["core_cli_declared"] is True
    assert result["shared_skill_count"] >= 10
    assert result["full_parity"] is True
    assert "copilot" in result["hosts"]  # type: ignore[operator]
