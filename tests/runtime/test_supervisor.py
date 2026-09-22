from pathlib import Path

from apiforge.runtime.runner import run_runtime
from tests.runtime.test_runtime import make_task


def test_supervisor_returns_a_terminal_review_boundary(tmp_path: Path) -> None:
    make_task(tmp_path)
    result = run_runtime(tmp_path, "evolve-orders-api")
    assert result["status"] in {"REVIEW", "BLOCKED", "DONE"}
