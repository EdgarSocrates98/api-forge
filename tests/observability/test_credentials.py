import pytest

from apiforge.observability.credentials import check_reference, execute_read_gate, reference
from apiforge.observability.read import build_read_plan


def test_credential_check_never_reads_secret_values() -> None:
    status = check_reference("datadog", "DD_API_KEY", "env")

    assert status.status == "blocked"
    assert "no secret was read" in status.reason
    assert "DD_API_KEY" in status.reference


def test_read_gate_blocks_without_available_broker() -> None:
    plan = build_read_plan("dynatrace", "orders", "start", "end")
    status = check_reference("dynatrace", "DYNATRACE_TOKEN")

    receipt = execute_read_gate(plan, status)

    assert receipt.status == "blocked"
    assert receipt.network_called is False
    assert receipt.mutation_performed is False


def test_reference_rejects_empty_secret_reference() -> None:
    with pytest.raises(ValueError, match="AF-OBS-CREDENTIAL-REFERENCE"):
        reference("cloudwatch", "")
