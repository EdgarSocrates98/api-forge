"""§40–§43 deterministic evals: audit findings, disclosure routing, paging."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.mcp.audit import audit_surface
from apiforge.mcp.benchmark import benchmark_tools
from apiforge.mcp.disclosure import disclose
from apiforge.output.page import paged


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError("AF-EVALS-INVALID", f"tool-surface corpus {corpus} empty or duplicated")
    return cases


def _check_audit(case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("audit") or {}
    if not expect:
        return
    report = audit_surface()
    kinds = {finding.kind for finding in report.findings}
    for kind in expect.get("kinds") or ():
        if kind not in kinds:
            failures.append(f"audit kind {kind} absent")
    for kind in expect.get("absent") or ():
        if kind in kinds:
            failures.append(f"audit kind {kind} unexpectedly present")
    if "max_findings" in expect and len(report.findings) > int(expect["max_findings"]):
        failures.append(f"{len(report.findings)} findings > {expect['max_findings']}")
    accepted = {(finding.tool, finding.kind) for finding in report.accepted}
    for row in expect.get("accepted") or ():
        pair = (row.get("tool"), row.get("kind"))
        if pair not in accepted:
            failures.append(f"audit accepted {pair} missing")
    for item in expect.get("unresolved") or ():
        if not any(item in entry for entry in report.unresolved):
            failures.append(f"audit unresolved missing {item!r}")


def _check_disclose(case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("disclose") or {}
    if not expect:
        return
    result = disclose(expect["task"])
    if "task_class" in expect and result.task_class != expect["task_class"]:
        failures.append(f"task_class {result.task_class} != {expect['task_class']}")
    for name in expect.get("active") or ():
        if name not in result.active_tools:
            failures.append(f"active tool {name} missing")
    for name in expect.get("dropped") or ():
        if name not in result.dropped_tools:
            failures.append(f"dropped tool {name} missing")


def _check_paged(case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("paged") or {}
    if not expect:
        return
    page = paged(
        list(range(int(expect["items"]))),
        offset=int(expect.get("offset", 0)),
        limit=int(expect.get("limit", 50)),
    )
    if page.pagination.total != int(expect["items"]):
        failures.append(f"total {page.pagination.total} != {expect['items']}")
    wanted_next = expect.get("next_offset", "__missing__")
    if wanted_next != "__missing__" and page.pagination.next_offset != wanted_next:
        failures.append(f"next_offset {page.pagination.next_offset} != {wanted_next}")
    if "shown" in expect and len(page.items) != int(expect["shown"]):
        failures.append(f"shown {len(page.items)} != {expect['shown']}")


def _check_benchmark(case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("benchmark") or {}
    if not expect:
        return
    samples = {
        str(name): {"kwargs": dict(spec.get("kwargs") or {})}
        for name, spec in (expect.get("samples") or {}).items()
    }
    report = benchmark_tools(samples, repeats=int(expect.get("repeats", 1)))
    measured = {item.tool for item in report.tools}
    for name in expect.get("measured") or ():
        if name not in measured:
            failures.append(f"benchmark tool {name} not measured")
    for item in expect.get("unresolved") or ():
        if not any(item in entry for entry in report.unresolved):
            failures.append(f"benchmark unresolved missing {item!r}")


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    _check_audit(case, failures)
    _check_disclose(case, failures)
    _check_paged(case, failures)
    _check_benchmark(case, failures)
    return {"id": case["id"], "passed": not failures, "failures": failures}


def run_tool_surface(corpus: Path) -> dict[str, Any]:
    cases = load_cases(corpus)
    results = [_run_case(case) for case in cases]
    failed = [result["id"] for result in results if not result["passed"]]
    return {
        "schema": "apiforge/tool-surface-evals/v1",
        "corpus": str(corpus),
        "cases": results,
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["load_cases", "run_tool_surface"]
