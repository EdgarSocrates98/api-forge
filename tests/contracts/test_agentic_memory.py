from __future__ import annotations

import pytest
from pydantic import ValidationError

from apiforge.contracts.agentic_memory import MemoryRecord, SemanticCheckpoint


def test_memory_contract_is_closed_and_versioned() -> None:
    record = MemoryRecord(
        memory_id="memory:1234567890abcdef",
        scope="working",
        origin="tool_result",
        created_at="2026-10-04T10:00:00Z",
        payload={"answer": "data"},
        content_sha256="a" * 64,
    )
    assert record.version == 1
    with pytest.raises(ValidationError):
        MemoryRecord.model_validate(record.model_dump(mode="json") | {"unexpected": True})


def test_invalidated_memory_requires_actor_reference() -> None:
    with pytest.raises(ValidationError, match="invalidated_by"):
        MemoryRecord(
            memory_id="memory:1234567890abcdef",
            scope="working",
            origin="tool_result",
            created_at="2026-10-04T10:00:00Z",
            outcome="invalidated",
            payload={"answer": "data"},
            content_sha256="a" * 64,
        )


def test_semantic_checkpoint_preserves_unresolved_state() -> None:
    checkpoint = SemanticCheckpoint(
        checkpoint_id="checkpoint:1234567890abcdef",
        task_id="task-1",
        run_id="run-1",
        task_state="blocked",
        current_objective="resume safely",
        unresolved=("AF-BUDGET-EXHAUSTED",),
        created_at="2026-10-04T10:00:00Z",
        content_sha256="b" * 64,
    )
    assert checkpoint.unresolved == ("AF-BUDGET-EXHAUSTED",)
