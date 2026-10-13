"""Judge catalog ``check`` rules against fact kinds — findings cite fact_ids."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from apiforge.core.ids import stable_id
from apiforge.core.models import Fact, Finding, FindingStatus
from apiforge.rules.catalog import load_catalog


def _resolve(fact: Fact, path: str) -> tuple[bool, Any]:
    node: Any = {"measures": fact.measures, "attrs": fact.attrs}
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return False, None
        node = node[part]
    return True, node


def _matches(op: str, found: bool, actual: Any, expected: Any) -> bool:
    if op == "present":
        return found
    if op == "absent":
        return not found
    if not found:
        return False
    if op == "eq":
        return bool(actual == expected)
    if op == "ne":
        return bool(actual != expected)
    try:
        a, e = float(actual), float(expected)
    except (TypeError, ValueError):
        return False
    if op == "gt":
        return a > e
    if op == "ge":
        return a >= e
    if op == "lt":
        return a < e
    if op == "le":
        return a <= e
    return False


def judge_facts(facts: Iterable[Fact]) -> tuple[Finding, ...]:
    """Apply every catalog rule with a ``check`` block to the given facts."""
    checks = [meta for meta in load_catalog().values() if meta.check is not None]
    findings: list[Finding] = []
    for fact in facts:
        for meta in checks:
            check = meta.check
            assert check is not None
            if fact.kind != check.kind:
                continue
            found, actual = _resolve(fact, check.path)
            if not _matches(check.op, found, actual, check.value):
                continue
            findings.append(
                Finding(
                    finding_id=stable_id("finding", {"rule": meta.rule_id, "fact": fact.fact_id}),
                    rule_id=meta.rule_id,
                    status=FindingStatus.CONFIRMED,
                    severity=meta.severity,
                    title=meta.title,
                    detail=f"{fact.kind}: {check.path}={actual!r} ({check.op} {check.value!r})",
                    evidence=(fact.fact_id,),
                    remediation=meta.remediation,
                )
            )
    return tuple(findings)
