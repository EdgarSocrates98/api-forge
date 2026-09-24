from pathlib import Path

from apiforge.tui.fallback import render_fallback
from tests.runtime.test_runtime import make_task


def test_fallback_exposes_same_projection_and_unlock(tmp_path: Path) -> None:
    make_task(tmp_path)
    payload = render_fallback(tmp_path, "evolve-orders-api", emit=False)
    assert payload["code"] == "AF-TUI-UNAVAILABLE"
    assert payload["view"]["task_id"] == "evolve-orders-api"
    assert payload["view"]["status"] == "REVIEW"
