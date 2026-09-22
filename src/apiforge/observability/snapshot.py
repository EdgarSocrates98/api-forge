"""Content-addressed observation snapshots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apiforge.contracts.observability import ObservationSnapshot, TelemetryRecord


def snapshot(records: tuple[TelemetryRecord, ...], environment: str = "local", observed_at: str | None = None) -> ObservationSnapshot:
    payload = [record.model_dump(mode="json") for record in records]
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return ObservationSnapshot(
        snapshot_id=f"snapshot:{digest[:16]}",
        environment=environment,
        observed_at=observed_at,
        records=records,
        digest=digest,
        provenance=tuple(sorted({record.source for record in records})),
    )


def save_snapshot(root: Path, value: ObservationSnapshot) -> Path:
    target = root / ".apiforge" / "observability" / f"{value.snapshot_id.replace(':', '-')}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value.model_dump(mode="json"), sort_keys=True, indent=2), encoding="utf-8")
    return target
