"""§53–§57 deterministic evals: seeded ledgers -> inspect/compare/waste verdicts."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import yaml

from apiforge.agentops.compare import compare_runs
from apiforge.agentops.inspect import inspect_run
from apiforge.agentops.waste import detect_waste
from apiforge.contracts.base import ContractError
from apiforge.contracts.economy import CostVector, LedgerRef, RunLedgerEntry
from apiforge.contracts.token_economics import TokenLedgerEntry
from apiforge.economy import run_ledger, token_ledger
from apiforge.economy.token_ledger import entry_id, transcript_accounting


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError("AF-EVALS-INVALID", f"agentops corpus {corpus} empty or duplicated")
    return cases


def _seed(root: Path, case: dict[str, Any]) -> None:
    for row in case.get("ledger") or ():
        cost = row.get("cost") or {}
        run_ledger.append(
            root,
            RunLedgerEntry(
                run_id=row["run_id"],
                verb=row["verb"],
                source=row.get("source", "contract"),
                cost=CostVector(**cost),
                refs=tuple(
                    LedgerRef(
                        uri=f"ctx://sha256/{ref['hash'] * 64}",
                        label=ref.get("label", "ref"),
                        provenance=ref.get("provenance", "eval"),
                        size_bytes=ref.get("size_bytes", 1),
                    )
                    for ref in row.get("refs") or ()
                ),
            ),
        )
    for row in case.get("usage") or ():
        accounting = transcript_accounting(
            row.get("model", "eval-model"), row.get("tokens", {}), recorded="eval"
        )
        token_ledger.append_usage(
            root,
            TokenLedgerEntry(
                run_id=row["run_id"],
                agent=row.get("agent"),
                task_id=row.get("task_id"),
                accounting=accounting,
                entry_id=entry_id(
                    row["run_id"],
                    accounting,
                    "eval",
                    model_call_id=row.get("model_call_id"),
                ),
                recorded_at="eval",
                model_call_id=row.get("model_call_id"),
            ),
        )


def _check_inspect(root: Path, case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("inspect") or {}
    if not expect:
        return
    report = inspect_run(root, case["run_id"], risk=case.get("risk"))

    def metric(section: str, name: str) -> Any:
        for item in report.sections:
            if item.name == section:
                for m in item.metrics:
                    if m.name == name:
                        return m
        return None

    for section, checks in (expect.get("metrics") or {}).items():
        for name, wanted in checks.items():
            got = metric(section, name)
            if got is None:
                failures.append(f"{section}.{name} missing")
                continue
            if isinstance(wanted, dict):
                if "value" in wanted and got.value != wanted["value"]:
                    failures.append(f"{section}.{name}={got.value} != {wanted['value']}")
                if "state" in wanted and got.state != wanted["state"]:
                    failures.append(f"{section}.{name}.state={got.state} != {wanted['state']}")
            elif got.value != wanted:
                failures.append(f"{section}.{name}={got.value} != {wanted}")
    for item in expect.get("unresolved") or ():
        if not any(item in entry for entry in report.unresolved):
            failures.append(f"unresolved missing {item!r}")
    wanted_sections = expect.get("sections")
    if wanted_sections is not None:
        got = [s.name for s in report.sections]
        if got != list(wanted_sections):
            failures.append(f"sections {got} != {wanted_sections}")


def _check_waste(root: Path, case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("waste") or {}
    if not expect:
        return
    report = detect_waste(root, case["run_id"], risk=case.get("risk"))
    kinds = {finding.kind: finding.evidence for finding in report.findings}
    for kind, evidence in (expect.get("findings") or {}).items():
        if kind not in kinds:
            failures.append(f"waste {kind} not detected")
        elif evidence and kinds[kind] != evidence:
            failures.append(f"waste {kind} evidence {kinds[kind]} != {evidence}")
    for kind in expect.get("absent") or ():
        if kind in kinds:
            failures.append(f"waste {kind} unexpectedly detected")
    for item in expect.get("unresolved") or ():
        if not any(item in entry for entry in report.unresolved):
            failures.append(f"waste unresolved missing {item!r}")


def _check_compare(root: Path, case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("compare") or {}
    if not expect:
        return
    result = compare_runs(root, expect["run_a"], expect["run_b"])
    verdicts = {axis.axis: axis.verdict for axis in result.axes}
    for axis, wanted in (expect.get("verdicts") or {}).items():
        if verdicts.get(axis) != wanted:
            failures.append(f"axis {axis}={verdicts.get(axis)} != {wanted}")


def _run_case(case: dict[str, Any], root: Path) -> dict[str, Any]:
    _seed(root, case)
    failures: list[str] = []
    _check_inspect(root, case, failures)
    _check_waste(root, case, failures)
    _check_compare(root, case, failures)
    return {"id": case["id"], "passed": not failures, "failures": failures}


def run_agentops(corpus: Path) -> dict[str, Any]:
    cases = load_cases(corpus)
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="af-agentops-evals-") as tmp:
        for index, case in enumerate(cases):
            results.append(_run_case(case, Path(tmp) / str(index)))
    failed = [result["id"] for result in results if not result["passed"]]
    return {
        "schema": "apiforge/agentops-evals/v1",
        "corpus": str(corpus),
        "cases": results,
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["load_cases", "run_agentops"]
