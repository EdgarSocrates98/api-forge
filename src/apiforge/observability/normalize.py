"""Convert supported fixture shapes into canonical telemetry records."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from typing import cast

from apiforge.contracts.observability import SignalKind, TelemetryRecord
from apiforge.observability.redaction import normalize_route, redact_attributes


def normalize_records(
    records: Iterable[Mapping[str, object]], source: str = "fixture"
) -> tuple[TelemetryRecord, ...]:
    normalized: list[TelemetryRecord] = []
    for index, item in enumerate(records):
        attributes = item.get("attributes")
        attrs = attributes if isinstance(attributes, Mapping) else {}
        operation = item.get("operation") or item.get("http.route")
        payload = json.dumps(dict(item), sort_keys=True, default=str).encode("utf-8")
        normalized.append(
            TelemetryRecord(
                id=str(item.get("id") or hashlib.sha256(payload).hexdigest()[:16]),
                kind=cast(SignalKind, str(item.get("kind") or "span")),
                service=str(item.get("service") or "unknown"),
                operation=normalize_route(str(operation)) if operation else None,
                timestamp=str(item.get("timestamp")) if item.get("timestamp") else None,
                duration_ms=float(str(item["duration_ms"]))
                if item.get("duration_ms") is not None
                else None,
                status_code=int(str(item["status_code"]))
                if item.get("status_code") is not None
                else None,
                value=float(str(item["value"])) if item.get("value") is not None else None,
                attributes=redact_attributes(attrs),
                source=source,
                source_hash=hashlib.sha256(payload).hexdigest(),
            )
        )
    return tuple(normalized)
