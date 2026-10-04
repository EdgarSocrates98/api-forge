"""Deterministic context-quality evals: fixture capsule + recorded uses ->
metric catalog and minimum-sufficient decision vs declared expectations."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from apiforge.context.quality import evaluate
from apiforge.context.sufficiency import minimum_sufficient
from apiforge.contracts.base import ContractError
from apiforge.contracts.context import ContextRef
from apiforge.contracts.context_quality import ContextUseRecord


def _uri(case_id: str, index: int) -> str:
    return f"ctx://sha256/{hashlib.sha256(f'{case_id}:{index}'.encode()).hexdigest()}"


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"context-quality corpus {corpus} empty or duplicated"
        )
    return cases


def _refs(case: dict[str, Any]) -> tuple[ContextRef, ...]:
    refs: list[ContextRef] = []
    for index, spec in enumerate(case.get("refs") or ()):
        refs.append(
            ContextRef(
                uri=_uri(case["id"], index),
                kind=spec["kind"],
                label=spec.get("label", f"ref {index}"),
                source=spec.get("source", f"source-{index}"),
                span=tuple(spec["span"]) if spec.get("span") else None,
                size_bytes=int(spec.get("size_bytes", 64)),
                provenance=spec.get("provenance", "eval-fixture"),
                origin=spec["origin"],
                level=spec.get("level", "L3"),
                parity=spec.get("parity"),
            )
        )
    return tuple(refs)


def _uses(case: dict[str, Any], refs: tuple[ContextRef, ...]) -> tuple[ContextUseRecord, ...]:
    uses: list[ContextUseRecord] = []
    for index, spec in enumerate(case.get("uses") or ()):
        uri = refs[int(spec["uri_index"])].uri if "uri_index" in spec else str(spec["uri"])
        uses.append(
            ContextUseRecord(
                use_id=f"{case['id']}:{index}",
                run_id=case.get("run_id", case["id"]),
                ref_uri=uri,
                action=spec["action"],
                role=spec.get("role"),
                bytes=int(spec.get("bytes", 0)),
                tokens=spec.get("tokens"),
            )
        )
    return tuple(uses)


def _metric_check(name: str, metric: Any, expect: dict[str, Any], failures: list[str]) -> None:
    if "basis" in expect and metric.basis != expect["basis"]:
        failures.append(f"{name}: basis {metric.basis} != {expect['basis']}")
        return
    if metric.basis == "unresolved" and ("min" in expect or "max" in expect or "value" in expect):
        failures.append(f"{name}: unresolved but expectations declared")
        return
    value = metric.value or 0.0
    if "value" in expect and abs(value - float(expect["value"])) > 1e-4:
        failures.append(f"{name}: {value} != {expect['value']}")
    if "min" in expect and value < float(expect["min"]):
        failures.append(f"{name}: {value} < min {expect['min']}")
    if "max" in expect and value > float(expect["max"]):
        failures.append(f"{name}: {value} > max {expect['max']}")


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    refs = _refs(case)
    uses = _uses(case, refs)
    run_id = case.get("run_id", case["id"])
    required = {
        refs[int(index)].uri if isinstance(index, int) else str(index)
        for index in case.get("required_uris") or ()
    }
    report = evaluate(
        refs,
        uses,
        run_id=run_id,
        required_uris=required,
        cache_hits=case.get("cache_hits"),
        cache_lookups=case.get("cache_lookups"),
    )
    sufficiency = minimum_sufficient(
        refs,
        uses,
        run_id=run_id,
        required_uris=required,
        gate=case.get("gate", "strict"),
    )
    failures: list[str] = []
    expect = case.get("expect") or {}
    if "status" in expect and report.status != expect["status"]:
        failures.append(f"status {report.status} != {expect['status']}")
    by_name = {metric.name: metric for metric in report.metrics}
    for name, spec in (expect.get("metrics") or {}).items():
        if name not in by_name:
            failures.append(f"missing metric {name}")
            continue
        _metric_check(name, by_name[name], spec or {}, failures)
    expect_suff = expect.get("sufficiency")
    if expect_suff is not None:
        if "sufficient" in expect_suff and sufficiency.sufficient != expect_suff["sufficient"]:
            failures.append(f"sufficient {sufficiency.sufficient} != {expect_suff['sufficient']}")
        if (
            "pruned_count" in expect_suff
            and len(sufficiency.pruned_refs) != expect_suff["pruned_count"]
        ):
            failures.append(
                f"pruned {len(sufficiency.pruned_refs)} != {expect_suff['pruned_count']}"
            )
        if (
            "pruned_bytes" in expect_suff
            and sufficiency.pruned_bytes != expect_suff["pruned_bytes"]
        ):
            failures.append(
                f"pruned_bytes {sufficiency.pruned_bytes} != {expect_suff['pruned_bytes']}"
            )
    return {
        "id": case["id"],
        "passed": not failures,
        "failures": failures,
        "status": report.status,
        "metrics": {name: m.model_dump(mode="json") for name, m in by_name.items()},
        "sufficiency": sufficiency.model_dump(
            mode="json", exclude={"metrics_before", "metrics_after"}
        ),
    }


def run_context_quality(corpus: Path) -> dict[str, Any]:
    cases = load_cases(corpus)
    results = [_run_case(case) for case in cases]
    failed = [result["id"] for result in results if not result["passed"]]
    return {
        "schema": "apiforge/evals-context-quality/v1",
        "corpus": str(corpus),
        "cases": results,
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["run_context_quality"]
