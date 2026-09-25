from pathlib import Path

from apiforge.application.experience_projection import project_status
from apiforge.runtime.runner import run_runtime
from apiforge.tui.fallback import render_fallback
from tests.runtime.test_runtime import make_task


def test_json_and_fallback_share_canonical_view(tmp_path: Path) -> None:
    make_task(tmp_path)
    run_runtime(tmp_path, "evolve-orders-api", now="2026-09-25T10:02:00+00:00")
    snapshot = project_status(tmp_path, "evolve-orders-api")
    fallback = render_fallback(tmp_path, "evolve-orders-api", emit=False)
    assert fallback["view"] == snapshot.model_dump(mode="json")["view"]
    assert snapshot.view.payload["routing"]["risk_complexity"]["complexity"] == "moderate"
