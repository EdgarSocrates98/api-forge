"""Deterministic budgets for provider read responses."""

from __future__ import annotations

import json
from collections.abc import Mapping

from apiforge.contracts.observability import ReadSafetyPolicy


def response_size_bytes(response: Mapping[str, object]) -> int:
    payload = json.dumps(response, default=str, sort_keys=True, separators=(",", ":"))
    return len(payload.encode("utf-8"))


def evaluate_response(
    policy: ReadSafetyPolicy, response: Mapping[str, object]
) -> tuple[int, int, tuple[str, ...]]:
    records = response.get("records", ())
    record_count = len(records) if isinstance(records, (list, tuple)) else 0
    size = response_size_bytes(response)
    violations: list[str] = []
    if record_count > policy.max_records:
        violations.append(f"max_records_exceeded:{record_count}>{policy.max_records}")
    if size > policy.max_response_bytes:
        violations.append(f"max_response_bytes_exceeded:{size}>{policy.max_response_bytes}")
    return record_count, size, tuple(violations)
