from __future__ import annotations

from pathlib import Path

from apiforge.observability.change_metrics import (
    ChangeRunMetrics,
    ChangeStageMetric,
    write_change_metrics,
)


def test_change_metrics_record_source_status_and_artifacts(tmp_path: Path) -> None:
    metrics = ChangeRunMetrics(
        run_id="run",
        source="artifact",
        repository="example/repo",
        base_sha="0" * 40,
        head_sha="1" * 40,
        status="review",
        stages=(ChangeStageMetric(stage="analyze", duration_ms=1, status="ok"),),
        artifact_refs=("case.json",),
    )
    path = tmp_path / "metrics.json"
    write_change_metrics(path, metrics)
    assert "artifact" in path.read_text(encoding="utf-8")
