"""Economy benchmark: capsule bytes and evidence recall against a recorded baseline.

The baseline models today's agent path — the ``context resolve`` payload plus
every file that holds required evidence, read whole. The capsule side is
charged the capsule itself plus a full expansion of every ref it carries, so
the reduction is a conservative bound. Quality is a floor, never traded:
capsule recall must match baseline recall in every case.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import statistics
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from apiforge.context.gateway.canonical import dumps
from apiforge.context.gateway.errors import GatewayError

BASELINE_FILE = "baseline.json"
DEFAULT_MIN_REDUCTION = 0.40
_IGNORED = shutil.ignore_patterns(".apiforge", "__pycache__", "*.pyc", "conftest.py")


@dataclass(frozen=True)
class RequiredRef:
    path: str
    symbol: str
    kind: str | None = None


@dataclass(frozen=True)
class EconomyCase:
    case_id: str
    fixture: str
    contract: str
    target: str
    required_refs: tuple[RequiredRef, ...]
    level: str = "L3"
    budget_bytes: int = 16000


def load_corpus(corpus: Path) -> list[EconomyCase]:
    cases: list[EconomyCase] = []
    for path in sorted(Path(corpus).glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        cases.append(
            EconomyCase(
                case_id=str(raw["id"]),
                fixture=str(raw["fixture"]),
                contract=str(raw["contract"]),
                target=str(raw["target"]),
                level=str(raw.get("level", "L3")),
                budget_bytes=int(raw.get("budget_bytes", 16000)),
                required_refs=tuple(
                    RequiredRef(str(item["path"]), str(item["symbol"]), item.get("kind"))
                    for item in raw.get("required_refs") or []
                ),
            )
        )
    ids = [case.case_id for case in cases]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if not cases or duplicates:
        raise _error(
            "AF-EVALS-INVALID",
            f"economy corpus {corpus} is empty or has duplicate ids {duplicates}",
            "corpus",
            "add uniquely named case yaml files under the corpus directory",
        )
    return cases


def materialize(case: EconomyCase, repo_root: Path, workdir: Path) -> tuple[Path, str]:
    root = workdir / case.case_id
    shutil.copytree(repo_root / case.fixture, root / "proj", ignore=_IGNORED)
    shutil.copyfile(repo_root / case.contract, root / "openapi.yaml")
    digest = _tree_digest(root)
    from apiforge.application.analyze import analyze_project

    analyze_project(root / "openapi.yaml", root / "proj", None, root / ".apiforge" / "case")
    return root, digest


def measure_baseline(case: EconomyCase, root: Path) -> dict[str, Any]:
    from apiforge.application.context import resolve_context

    resolved = resolve_context(root, scope="repo")
    payload = resolved.model_dump(mode="json") if hasattr(resolved, "model_dump") else resolved
    text = json.dumps(payload, sort_keys=True, ensure_ascii=True, indent=2)
    text = text.replace(json.dumps(str(root))[1:-1], ".")
    files = {ref.path: (root / ref.path) for ref in case.required_refs}
    contents = {
        path: file.read_text(encoding="utf-8") for path, file in files.items() if file.is_file()
    }
    found = [ref for ref in case.required_refs if ref.symbol in contents.get(ref.path, "")]
    return {
        "baseline_bytes": len(text.encode("utf-8"))
        + sum(len(t.encode("utf-8")) for t in contents.values()),
        "baseline_recall": _ratio(len(found), len(case.required_refs)),
    }


def measure_capsule(case: EconomyCase, root: Path) -> dict[str, Any]:
    from apiforge.context.gateway.capsule import build_capsule, emit
    from apiforge.context.gateway.refs import CtxStore

    first = build_capsule(root, case.target, budget_bytes=case.budget_bytes, max_level=case.level)  # type: ignore[arg-type]
    second = build_capsule(root, case.target, budget_bytes=case.budget_bytes, max_level=case.level)  # type: ignore[arg-type]
    capsule_bytes = len(dumps(emit(first)))
    store = CtxStore(root)
    contents = {ref.uri: store.get(ref.uri) for ref in first.refs}
    expanded = sum(ref.size_bytes for ref in first.refs)
    missing = [
        f"{ref.path}#{ref.symbol}"
        for ref in case.required_refs
        if not any(
            item.source == ref.path
            and (ref.kind is None or item.kind == ref.kind)
            and ref.symbol in contents[item.uri]
            for item in first.refs
        )
    ]
    return {
        "status": first.status,
        "capsule_bytes": capsule_bytes,
        "expanded_bytes": expanded,
        "effective_bytes": capsule_bytes + expanded,
        "refs": len(first.refs),
        "capsule_recall": _ratio(len(case.required_refs) - len(missing), len(case.required_refs)),
        "missing_evidence": missing,
        "deterministic": dumps(emit(first)) == dumps(emit(second)),
        "run_id": first.run_id,
    }


def record_baseline(corpus: Path, repo_root: Path) -> dict[str, Any]:
    cases = load_corpus(corpus)
    recorded: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="af-economy-") as tmp:
        for case in cases:
            root, digest = materialize(case, repo_root, Path(tmp))
            recorded[case.case_id] = {"fixture_sha256": digest, **measure_baseline(case, root)}
    document = {"schema": "apiforge/economy-baseline/v1", "cases": dict(sorted(recorded.items()))}
    (Path(corpus) / BASELINE_FILE).write_text(
        json.dumps(document, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return document


def run_economy(
    corpus: Path,
    repo_root: Path,
    *,
    min_reduction: float = DEFAULT_MIN_REDUCTION,
    measure: Callable[[EconomyCase, Path], dict[str, Any]] = measure_capsule,
) -> dict[str, Any]:
    cases = load_corpus(corpus)
    baseline = _load_baseline(Path(corpus), cases)
    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="af-economy-") as tmp:
        for case in cases:
            root, digest = materialize(case, repo_root, Path(tmp))
            recorded = baseline[case.case_id]
            if recorded["fixture_sha256"] != digest:
                raise _error(
                    "AF-EVALS-ECONOMY-BASELINE-STALE",
                    f"{case.case_id}: fixture changed since the baseline was recorded",
                    "baseline.json",
                    "rerun `apiforge evals economy --record-baseline` and commit the new baseline",
                )
            rows.append(_row(case, recorded, measure(case, root)))
    return summarize(rows, min_reduction)


def summarize(rows: list[dict[str, Any]], min_reduction: float) -> dict[str, Any]:
    reductions = [row["reduction"] for row in rows]
    median = round(statistics.median(reductions), 4) if reductions else 0.0
    quality_failures = [
        row["case_id"] for row in rows if row["capsule_recall"] < row["baseline_recall"]
    ]
    nondeterministic = [row["case_id"] for row in rows if not row["deterministic"]]
    gates = {
        "baseline_recorded": bool(rows),
        "quality_floor": not quality_failures,
        "median_reduction": median >= min_reduction,
        "deterministic": not nondeterministic,
    }
    return {
        "schema": "apiforge/economy-eval/v1",
        "cases": len(rows),
        "median_reduction": median,
        "min_reduction": min_reduction,
        "quality_failures": quality_failures,
        "nondeterministic": nondeterministic,
        "gates": gates,
        "passed": all(gates.values()),
        "rows": rows,
        "tokens": "unresolved",
    }


def _row(
    case: EconomyCase, recorded: Mapping[str, Any], measured: Mapping[str, Any]
) -> dict[str, Any]:
    baseline_bytes = int(recorded["baseline_bytes"])
    effective = int(measured["effective_bytes"])
    return {
        "case_id": case.case_id,
        "target": case.target,
        "baseline_bytes": baseline_bytes,
        "baseline_recall": float(recorded["baseline_recall"]),
        **measured,
        "reduction": round(1 - effective / baseline_bytes, 4) if baseline_bytes else 0.0,
    }


def _load_baseline(corpus: Path, cases: list[EconomyCase]) -> dict[str, Any]:
    path = corpus / BASELINE_FILE
    recorded = (
        json.loads(path.read_text(encoding="utf-8")).get("cases", {}) if path.is_file() else {}
    )
    missing = sorted(case.case_id for case in cases if case.case_id not in recorded)
    if missing:
        raise _error(
            "AF-EVALS-ECONOMY-BASELINE-MISSING",
            f"no recorded baseline for {missing}",
            "baseline.json",
            "run `apiforge evals economy --record-baseline` before measuring the gateway",
        )
    return dict(recorded)


def _tree_digest(root: Path) -> str:
    hasher = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        hasher.update(path.relative_to(root).as_posix().encode("utf-8"))
        hasher.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return hasher.hexdigest()


def _ratio(found: int, total: int) -> float:
    return round(found / total, 4) if total else 1.0


def _error(code: str, detail: str, field: str, unlock: str) -> GatewayError:
    return GatewayError(code, detail, field=field, unlock=unlock)


__all__ = [
    "BASELINE_FILE",
    "DEFAULT_MIN_REDUCTION",
    "EconomyCase",
    "RequiredRef",
    "load_corpus",
    "measure_baseline",
    "measure_capsule",
    "record_baseline",
    "run_economy",
    "summarize",
]
