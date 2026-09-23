"""Run metrics for the API/Git/CI change-control pipeline."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.core.io import write_json
from apiforge.core.models import JsonValue


class ChangeStageMetric(VersionedContract):
    stage: Literal["collect", "analyze", "next_step", "graph", "evidence", "brief", "evaluate"]
    duration_ms: float = Field(ge=0)
    status: Literal["ok", "review", "blocked", "failed"]
    error_code: str | None = None


class ChangeRunMetrics(VersionedContract):
    """Stable operational envelope; durations are observations, not claims."""

    run_id: str
    source: str
    repository: str
    base_sha: str
    head_sha: str
    status: Literal["ok", "review", "blocked", "failed"]
    unresolved: tuple[str, ...] = ()
    adapter_errors: tuple[str, ...] = ()
    artifact_refs: tuple[str, ...] = ()
    stages: tuple[ChangeStageMetric, ...] = ()
    details: Mapping[str, JsonValue] = Field(default_factory=dict)


def write_change_metrics(path: Path, metrics: ChangeRunMetrics) -> None:
    write_json(path, metrics)
