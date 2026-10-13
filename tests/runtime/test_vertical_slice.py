from pathlib import Path

from apiforge.runtime.runner import run_runtime
from tests.runtime.test_runtime import make_task


def test_existing_api_evolution_vertical_slice(tmp_path: Path) -> None:
    make_task(tmp_path)
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-22T12:00:00+00:00")
    assert result["run"]["revision"] == 1
    assert Path(str(result["run_dir"])).is_dir()
