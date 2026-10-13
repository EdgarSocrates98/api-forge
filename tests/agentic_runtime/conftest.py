"""Shared local fixtures for TaskSpec, verification and holdout tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from apiforge.report.keys import generate_keypair
from apiforge.taskspec.compiler import compile_intent
from apiforge.taskspec.service import create_task, review_task, seal_task

FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "orders_agentic"


@pytest.fixture
def orders_paths() -> dict[str, Path]:
    return {
        "contract": FIXTURE_ROOT / "openapi.yaml",
        "project": FIXTURE_ROOT,
        "manifest": FIXTURE_ROOT / "mutations.yaml",
        "data": FIXTURE_ROOT / "data.json",
    }


@pytest.fixture
def sealed_task(tmp_path: Path, orders_paths: dict[str, Path]) -> tuple[Path, str]:
    task_root = tmp_path / "tasks"
    (tmp_path / "case").mkdir()
    spec = compile_intent(
        "orders-verified",
        "verify the Commerce Orders API",
        contract=orders_paths["contract"],
        project=orders_paths["project"],
        case=tmp_path / "case",
    )
    create_task(task_root, spec)
    review_task(task_root, spec.id, "planner")
    key_path = tmp_path / "keys" / "sealer.pem"
    generate_keypair(key_path.parent, "sealer")
    seal_task(task_root, spec.id, key_path, "planner")
    return task_root, spec.id
