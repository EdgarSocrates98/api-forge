"""Cache eval (economy wave 2): reuse only what is still true, invalidate only what changed.

Each case materializes a fixture, warms a capsule selection for every
operation, proves an unchanged rebuild is an all-hit byte-identical run,
applies one scripted mutation (optionally re-analyzing) and rebuilds. The
invalidated set is compared with the case's ground truth, and every reused
capsule is compared byte-for-byte with an uncached build: a reuse that
differs is a ``stale_reuse`` — the one number that must stay zero.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from apiforge.cache.errors import CacheError
from apiforge.contracts.cache import CacheDecision

_IGNORED = shutil.ignore_patterns(".apiforge", "__pycache__", "*.pyc", "conftest.py")
_REUSE = {"reuse", "reuse_warn"}


@dataclass(frozen=True)
class CacheCase:
    case_id: str
    fixture: str
    contract: str
    mutation_file: str | None
    mutation_append: str
    mutation_replace: tuple[str, str] | None
    reanalyze: bool
    expect_invalidated: tuple[str, ...]


def load_corpus(corpus: Path) -> list[CacheCase]:
    cases: list[CacheCase] = []
    for path in sorted(Path(corpus).glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        mutation = raw.get("mutation") or {}
        cases.append(
            CacheCase(
                case_id=str(raw["id"]),
                fixture=str(raw["fixture"]),
                contract=str(raw["contract"]),
                mutation_file=mutation.get("file"),
                mutation_append=str(mutation.get("append", "")),
                mutation_replace=(
                    (str(mutation["replace"]["old"]), str(mutation["replace"]["new"]))
                    if mutation.get("replace")
                    else None
                ),
                reanalyze=bool(raw.get("reanalyze", True)),
                expect_invalidated=tuple(sorted(raw.get("expect_invalidated") or ())),
            )
        )
    ids = [case.case_id for case in cases]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if not cases or duplicates:
        raise CacheError(
            "AF-EVALS-INVALID",
            f"cache corpus {corpus} is empty or has duplicate ids {duplicates}",
            field="corpus",
            unlock="add uniquely named case yaml files under the corpus directory",
        )
    return cases


def _analyze(root: Path) -> None:
    from apiforge.application.analyze import analyze_project

    analyze_project(root / "openapi.yaml", root / "proj", None, root / ".apiforge" / "case")


def _operations(root: Path) -> list[str]:
    ir = json.loads((root / ".apiforge" / "case" / "api-ir.json").read_text(encoding="utf-8"))
    return sorted(f"{op['method'].upper()} {op['path']}" for op in ir.get("operations") or [])


def _build(root: Path, target: str, *, cache: bool) -> tuple[bytes, CacheDecision | None]:
    from apiforge.context.gateway.canonical import dumps
    from apiforge.context.gateway.capsule import build_capsule, emit

    seen: list[CacheDecision] = []
    capsule = build_capsule(root, target, cache=cache, on_decision=seen.append)
    return dumps(emit(capsule)), (seen[0] if seen else None)


def run_case(case: CacheCase, repo_root: Path, workdir: Path) -> dict[str, Any]:
    root = workdir / case.case_id
    shutil.copytree(repo_root / case.fixture, root / "proj", ignore=_IGNORED)
    shutil.copyfile(repo_root / case.contract, root / "openapi.yaml")
    _analyze(root)
    targets = _operations(root)
    for target in targets:
        _build(root, target, cache=True)
    warm_hits = 0
    identical = True
    for target in targets:
        cached, decision = _build(root, target, cache=True)
        uncached, _ = _build(root, target, cache=False)
        warm_hits += int(decision is not None and decision.action in _REUSE)
        identical = identical and cached == uncached
    delta_targets: list[str] = []
    if case.mutation_file:
        path = root / case.mutation_file
        _mutate(path, case)
        from apiforge.context.delta import build_delta

        delta = build_delta(root, changed=[case.mutation_file])
        delta_targets = list(delta.capsule_targets)
    if case.reanalyze:
        _analyze(root)
    targets_after = _operations(root)
    invalidated: list[str] = []
    stale: list[str] = []
    reused = 0
    for target in targets_after:
        cached, decision = _build(root, target, cache=True)
        uncached, _ = _build(root, target, cache=False)
        if decision is not None and decision.action in _REUSE:
            reused += 1
            if cached != uncached:
                stale.append(target)
        else:
            invalidated.append(target)
        if cached != uncached:
            identical = False
    expected = set(case.expect_invalidated)
    got = set(invalidated)
    return {
        "case_id": case.case_id,
        "targets": len(targets),
        "warm_hit_rate": round(warm_hits / len(targets), 4) if targets else 1.0,
        "identical_bytes": identical,
        "invalidated": sorted(got),
        "expected_invalidated": sorted(expected),
        "precision": _ratio(len(got & expected), len(got)),
        "recall": _ratio(len(got & expected), len(expected)),
        "reused_after_change": reused,
        "stale_reuse": stale,
        "delta_targets": sorted(delta_targets),
        "delta_recall": _ratio(len(set(delta_targets) & expected), len(expected)),
    }


def _mutate(path: Path, case: CacheCase) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if case.mutation_replace is not None:
        old, new = case.mutation_replace
        if old not in text:
            raise CacheError(
                "AF-EVALS-INVALID",
                f"{case.case_id}: {old!r} not found in {path.name}",
                field="mutation.replace.old",
                unlock="point the mutation at text that exists in the fixture",
            )
        text = text.replace(old, new, 1)
    text += case.mutation_append
    path.write_text(text, encoding="utf-8", newline="\n")


def run_cache_eval(corpus: Path, repo_root: Path) -> dict[str, Any]:
    cases = load_corpus(corpus)
    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="af-cache-") as tmp:
        for case in cases:
            rows.append(run_case(case, Path(repo_root), Path(tmp)))
    return summarize(rows)


def summarize(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    stale = [row["case_id"] for row in rows if row["stale_reuse"]]
    gates = {
        "warm_hit_rate": all(row["warm_hit_rate"] == 1.0 for row in rows),
        "identical_bytes": all(row["identical_bytes"] for row in rows),
        "stale_reuse_zero": not stale,
        "invalidation_precision": all(row["precision"] == 1.0 for row in rows),
        "invalidation_recall": all(row["recall"] == 1.0 for row in rows),
        "delta_recall": all(row["delta_recall"] == 1.0 for row in rows),
    }
    return {
        "schema": "apiforge/cache-eval/v1",
        "cases": len(rows),
        "stale_reuse_cases": stale,
        "gates": gates,
        "passed": all(gates.values()),
        "rows": list(rows),
    }


def _ratio(found: int, total: int) -> float:
    return round(found / total, 4) if total else 1.0


__all__ = ["CacheCase", "load_corpus", "run_cache_eval", "run_case", "summarize"]
