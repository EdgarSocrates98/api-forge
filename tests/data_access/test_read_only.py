from __future__ import annotations

from apiforge.contracts.data_runtime import DataReadRequest
from apiforge.data_access.read_only import ReadOnlyDataAdapter


class Requester:
    def __init__(self) -> None:
        self.calls = 0

    def read(self, request: DataReadRequest) -> dict[str, object]:
        self.calls += 1
        return {"provider": request.provider, "records": 1}


def test_read_only_data_adapter_executes_host_injected_read() -> None:
    requester = Requester()
    receipt = ReadOnlyDataAdapter().execute(
        DataReadRequest(provider="rds", resource_ref="orders", operation="describe"), requester
    )
    assert receipt.status == "executed"
    assert receipt.network_called is True
    assert receipt.mutation_performed is False
    assert requester.calls == 1
    assert receipt.response_digest


def test_read_only_data_adapter_blocks_mutation_before_network() -> None:
    requester = Requester()
    receipt = ReadOnlyDataAdapter().execute(
        DataReadRequest(provider="kafka", resource_ref="orders", operation="produce"), requester
    )
    assert receipt.status == "blocked"
    assert receipt.network_called is False
    assert requester.calls == 0
