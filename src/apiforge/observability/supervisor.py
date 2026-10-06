"""Deterministic control-plane orchestration over fixture inputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from apiforge.contracts.observability import SLODefinition
from apiforge.observability.adapters.otel_json import read
from apiforge.observability.normalize import normalize_records
from apiforge.observability.signals import summarize
from apiforge.observability.slo import evaluate_slo
from apiforge.observability.snapshot import save_snapshot, snapshot


def run_fixture(
    root: Path, source: Path, service: str | None = None, slo: dict[str, Any] | None = None
) -> dict[str, object]:
    records = normalize_records(read(source), source=source.name)
    if service:
        records = tuple(record for record in records if record.service == service)
    observed = snapshot(records)
    snapshot_path = save_snapshot(root, observed)
    result: dict[str, object] = {
        "snapshot": observed.model_dump(mode="json"),
        "snapshot_path": str(snapshot_path),
        "signals": [item.model_dump(mode="json") for item in summarize(records)],
    }
    if slo:
        definition = SLODefinition.model_validate(slo)
        result["slo"] = evaluate_slo(definition, records).model_dump(mode="json")
    return result


def load_json(path: Path) -> dict[str, object]:
    return cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
