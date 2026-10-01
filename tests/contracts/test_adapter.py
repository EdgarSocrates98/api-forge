from __future__ import annotations

import pytest
from pydantic import ValidationError

from apiforge.contracts.adapter import AdapterCapability, AdapterExecution


def test_adapter_execution_normalizes_reproducibility_fields() -> None:
    execution = AdapterExecution(
        adapter_id="kafka-source",
        mode="static",
        evidence_level="heuristic",
        input_hashes=(("b.py", "b"), ("a.py", "a")),
        tools=("regex", "regex"),
        unresolved=("dynamic topic", "dynamic topic"),
    )

    assert execution.input_hashes == (("a.py", "a"), ("b.py", "b"))
    assert execution.tools == ("regex",)
    assert execution.unresolved == ("dynamic topic",)


def test_live_mutation_is_described_but_not_implicitly_approved() -> None:
    execution = AdapterExecution(
        adapter_id="aws",
        mode="live_mutation",
        evidence_level="observed",
        status="blocked",
        limitations=("approval required",),
    )

    assert execution.mode == "live_mutation"
    assert execution.status == "blocked"
    assert execution.evidence_refs == ()


def test_capability_does_not_claim_live_data_by_default() -> None:
    capability = AdapterCapability(
        adapter_id="rds",
        capability="sql-access-scan",
        mode="static",
        evidence_level="heuristic",
    )

    assert capability.supports_live_data is False
    assert capability.supports_mutation is False


def test_invalid_adapter_mode_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AdapterExecution(adapter_id="bad", mode="execute_anything")  # type: ignore[arg-type]
