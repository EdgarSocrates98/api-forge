from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.contracts.task import Recipe, TaskRisk
from apiforge.taskspec.compiler import compile_intent


def test_compile_intent_creates_verified_local_task(orders_paths: dict[str, Path], tmp_path: Path) -> None:
    spec = compile_intent(
        "orders-compile",
        "verify orders",
        contract=orders_paths["contract"],
        project=orders_paths["project"],
        case=tmp_path,
    )
    assert spec.strategy is Recipe.VERIFIED_API_SLICE
    assert spec.risk is TaskRisk.LOCAL_REVERSIBLE
    assert set(spec.tests) == {"contract", "security", "idempotency", "pagination"}


def test_compile_intent_refuses_missing_context(orders_paths: dict[str, Path], tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="AF-TASK-CONTEXT"):
        compile_intent(
            "orders-missing",
            "verify orders",
            contract=orders_paths["contract"],
            project=tmp_path / "missing-project",
            case=tmp_path,
        )
