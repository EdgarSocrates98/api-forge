"""Explicit memory applicability matching and freshness derivation."""

from __future__ import annotations

import re
from datetime import datetime

from apiforge.contracts.agentic_memory import MemoryRecord

_CONSTRAINT = re.compile(
    r"^(?P<key>[A-Za-z_][A-Za-z0-9_.-]*)(?P<operator>==|>=|<=|=|>|<)(?P<value>.+)$"
)


def effective_freshness(record: MemoryRecord, now: str | None) -> str:
    """Derive freshness without turning missing clock evidence into fresh state."""
    if record.expires_at and now:
        try:
            if datetime.fromisoformat(record.expires_at) <= datetime.fromisoformat(now):
                return "expired"
        except (TypeError, ValueError):
            return "unresolved"
    elif record.expires_at and not now:
        return "unresolved"
    return record.freshness


def _version(value: str) -> tuple[int, ...] | None:
    parts = re.findall(r"\d+", value)
    return tuple(int(part) for part in parts) if parts else None


def _compare(left: str, right: str, operator: str) -> bool:
    left_version = _version(left)
    right_version = _version(right)
    if left_version is not None and right_version is not None:
        if operator in {"=", "=="}:
            return left_version == right_version
        if operator == ">=":
            return left_version >= right_version
        if operator == "<=":
            return left_version <= right_version
        if operator == ">":
            return left_version > right_version
        return left_version < right_version
    lhs = left.lower()
    rhs = right.lower()
    if operator in {"=", "=="}:
        return lhs == rhs
    if operator == ">=":
        return lhs >= rhs
    if operator == "<=":
        return lhs <= rhs
    if operator == ">":
        return lhs > rhs
    return lhs < rhs


def _query_value(runtime: dict[str, str], key: str) -> str | None:
    aliases: tuple[str, ...] = (key,)
    if key == "python":
        aliases = ("python", "language_version")
    elif key == "framework":
        aliases = ("framework", "framework_version")
    for alias in aliases:
        if alias in runtime:
            return runtime[alias]
    return None


def _constraint_matches(constraint: str, runtime: dict[str, str]) -> bool:
    match = _CONSTRAINT.fullmatch(constraint.strip())
    if match is None:
        return constraint.strip().lower() in {value.lower() for value in runtime.values()}
    value = _query_value(runtime, match.group("key"))
    return value is not None and _compare(value, match.group("value"), match.group("operator"))


def runtime_match(
    record: MemoryRecord, runtime: dict[str, str]
) -> tuple[bool, float, tuple[str, ...]]:
    """Match structured runtime requirements; never compare constraints to query terms."""
    requirements = tuple(record.runtime_requirements.items())
    constraints = tuple(record.runtime_constraints)
    total = len(requirements) + len(constraints)
    if not total:
        return True, 1.0, ()
    if not runtime:
        return True, 0.5, ()
    checks = [
        _query_value(runtime, key) is not None
        and _compare(_query_value(runtime, key) or "", value, "==")
        for key, value in requirements
    ]
    checks.extend(_constraint_matches(item, runtime) for item in constraints)
    matched = sum(checks)
    unresolved = tuple(
        f"runtime_mismatch:{key}={value}"
        for (key, value), check in zip(requirements, checks)
        if not check
    )
    unresolved += tuple(
        f"runtime_mismatch:{item}"
        for item, check in zip(constraints, checks[len(requirements) :])
        if not check
    )
    return matched == total, matched / total, unresolved


__all__ = ["effective_freshness", "runtime_match"]
