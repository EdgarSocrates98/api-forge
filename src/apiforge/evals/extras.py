"""Economy wave 7 eval: verification plans, retrieval, evidence refs, tiers, prefixes, locality.

Every case is deterministic and offline. Selection cases run on a
materialized ``economy_payments`` fixture; retrieval runs over the local
knowledge packs; tier and prefix cases need no fixture.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError

_IGNORED = shutil.ignore_patterns(".apiforge", "__pycache__", "*.pyc", "conftest.py")


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    rows = [
        yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [str(row.get("id")) for row in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"economy-extras corpus {corpus} empty or duplicated"
        )
    return rows


def _materialize(repo_root: Path, workdir: Path, fixture: str, contract: str) -> Path:
    from apiforge.application.analyze import analyze_project

    root = workdir / "fixture"
    if not (root / ".apiforge" / "case" / "case.json").is_file():
        shutil.copytree(repo_root / fixture, root / "proj", ignore=_IGNORED)
        shutil.copyfile(repo_root / contract, root / "openapi.yaml")
        analyze_project(root / "openapi.yaml", root / "proj", None, root / ".apiforge" / "case")
    return root


def _selection(case: dict[str, Any], root: Path) -> dict[str, Any]:
    from apiforge.verification.selection import plan_verification

    plan = plan_verification(
        root, case["changed"], risk=str(case["risk"]), breaking=bool(case.get("breaking"))
    )
    got = {item.path for item in plan.tests}
    expected = set(case.get("expect_tests") or ())
    ok = plan.level == case["expect_level"] and expected <= got
    if case.get("expect_fewer_than_all"):
        ok = ok and len(got) < plan.total_tests
    return {
        "level": plan.level,
        "tests": sorted(got),
        "total_tests": plan.total_tests,
        "passed": ok,
    }


def _retrieval(case: dict[str, Any], root: Path) -> dict[str, Any]:
    from apiforge.knowledge.retrieval import search

    result = search(str(case["query"]), store_root=root)
    packs = [item.pack_id for item in result.passages]
    ok = str(case["expect_pack"]) in packs
    if case.get("expect_expansion"):
        ok = ok and bool(result.added_terms)
    return {"top3": packs, "added_terms": list(result.added_terms), "passed": ok}


def _evidence(case: dict[str, Any], root: Path) -> dict[str, Any]:
    from apiforge.evidence.resolve import resolve

    node = resolve(root, str(case["ref"]))
    hop = [resolve(root, ref) for ref in node.neighbors]
    back = all(node.ref in item.neighbors for item in hop)
    ok = (
        bool(node.neighbors) and back and (not case.get("expect_source") or bool(hop[0].source_ref))
    )
    return {"neighbors": list(node.neighbors), "passed": ok}


def _tier(case: dict[str, Any]) -> dict[str, Any]:
    from apiforge.economy.providers import decide_tier

    decision = decide_tier(str(case["capability"]), str(case["risk"]), family=case.get("family"))
    return {
        "tier": decision.tier,
        "reason": decision.reason,
        "passed": decision.tier == case["expect_tier"],
    }


def _prefix(case: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    from apiforge.runtime.prompting import envelope

    first = envelope(
        repo_root, str(case["capability"]), task="task one", expertise=case.get("expertise", ())
    )
    second = envelope(
        repo_root, str(case["capability"]), task="task two", expertise=case.get("expertise", ())
    )
    other = envelope(repo_root, str(case["other_capability"]), task="task one")
    ok = (
        first.prefix_sha256 == second.prefix_sha256 != other.prefix_sha256
        and first.suffix != second.suffix
    )
    return {"prefix_sha256": first.prefix_sha256, "passed": ok}


def _doctor(case: dict[str, Any], root: Path) -> dict[str, Any]:
    from apiforge.economy.doctor import diagnose

    previous = os.environ.get("APIFORGE_CACHE")
    os.environ["APIFORGE_CACHE"] = "off"
    try:
        report = diagnose(root)
    finally:
        if previous is None:
            os.environ.pop("APIFORGE_CACHE", None)
        else:
            os.environ["APIFORGE_CACHE"] = previous
    codes = {item.code for item in report.findings}
    return {"codes": sorted(codes), "passed": str(case["expect_code"]) in codes}


def _locality(case: dict[str, Any], workdir: Path) -> dict[str, Any]:
    from apiforge.workspace.locality import plan_locality

    ws = workdir / "workspace"
    for repo in case["repositories"]:
        (ws / repo).mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "apiforge/workspace/v1",
        "workspace_id": "workspace:eval",
        "name": "eval",
        "root": ".",
        "repositories": [
            {"repository_id": f"repository:{name}", "name": name, "root": name}
            for name in case["repositories"]
        ],
        "relations": [
            {
                "relation": "depends_on",
                "source": "workspace.yaml",
                "from_id": f"repository:{a}",
                "to_id": f"repository:{b}",
            }
            for a, b in case["relations"]
        ],
    }
    (ws / "workspace.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    plan = plan_locality(ws, str(case["target"]))
    tiers = {tier.tier: list(tier.repositories) for tier in plan.tiers}
    ok = sorted(tiers["direct"]) == sorted(case["expect_direct"]) and plan.excluded == tuple(
        sorted(case.get("expect_excluded") or ())
    )
    return {"tiers": tiers, "excluded": list(plan.excluded), "passed": ok}


def run_extras(corpus: Path, repo_root: Path) -> dict[str, Any]:
    cases = load_cases(Path(corpus))
    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="af-extras-") as tmp:
        work = Path(tmp)
        for case in cases:
            kind = case["kind"]
            if kind in {"selection", "evidence", "doctor", "retrieval"}:
                root = _materialize(
                    Path(repo_root),
                    work,
                    case.get("fixture", "tests/fixtures/economy_payments/fastapi"),
                    case.get("contract", "tests/fixtures/economy_payments/openapi.yaml"),
                )
                if kind == "selection":
                    row = _selection(case, root)
                elif kind == "evidence":
                    row = _evidence(case, root)
                elif kind == "doctor":
                    row = _doctor(case, root)
                else:
                    row = _retrieval(case, root)
            elif kind == "tier":
                row = _tier(case)
            elif kind == "prefix":
                row = _prefix(case, Path(repo_root))
            elif kind == "locality":
                row = _locality(case, work)
            else:
                raise ContractError("AF-EVALS-INVALID", f"unknown case kind {kind!r}")
            rows.append({"case_id": case["id"], "kind": kind, **row})
    kinds = sorted({row["kind"] for row in rows})
    gates = {kind: all(row["passed"] for row in rows if row["kind"] == kind) for kind in kinds}
    return {
        "schema": "apiforge/economy-extras-eval/v1",
        "cases": len(rows),
        "gates": gates,
        "passed": all(gates.values()),
        "rows": rows,
    }


__all__ = ["load_cases", "run_extras"]
