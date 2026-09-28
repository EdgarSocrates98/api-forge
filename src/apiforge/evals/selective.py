"""Selective-agentics eval (economy wave 4): less context per agent, same evidence.

Case kinds (one yaml each under the corpus):

- ``expertise``: intent (+ capability/frameworks) → exact expected pack set;
- ``roles``: a fixture target and profile → per-role bytes from one capsule;
  subordinate roles must not exceed the primary and the total must stay under
  ``max_total_ratio`` of naive replication (full capsule to every role);
- ``debate``: scripted positions → referee packet ≤ ``max_packet_ratio`` of
  naive transport with every cited evidence id preserved.

Suite-level gates add shadow sampling accuracy per profile (10000 synthetic
run ids) and a deterministic agent audit with a verdict for every agent.
"""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

from apiforge.contracts.base import ContractError

_IGNORED = shutil.ignore_patterns(".apiforge", "__pycache__", "*.pyc", "conftest.py")
SHADOW_TOLERANCE = 0.02
SHADOW_SAMPLES = 10000


@dataclass(frozen=True)
class SelectiveCase:
    case_id: str
    kind: str
    raw: dict[str, Any]


def load_corpus(corpus: Path) -> list[SelectiveCase]:
    cases = []
    for path in sorted(Path(corpus).glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        cases.append(SelectiveCase(str(raw["id"]), str(raw["kind"]), raw))
    ids = [case.case_id for case in cases]
    bad = sorted({item for item in ids if ids.count(item) > 1}) or sorted(
        {c.case_id for c in cases if c.kind not in {"expertise", "roles", "debate"}}
    )
    if not cases or bad:
        raise ContractError(
            "AF-EVALS-INVALID", f"selective corpus {corpus} empty or invalid: {bad}"
        )
    return cases


def _expertise(case: SelectiveCase) -> dict[str, Any]:
    from apiforge.knowledge.selector import select_expertise

    raw = case.raw
    selection = select_expertise(
        str(raw["intent"]),
        capability=raw.get("capability"),
        frameworks=tuple(raw.get("frameworks") or ()),
    )
    got = {item.pack_id for item in selection.selected}
    expected = set(raw.get("expect_packs") or ())
    return {
        "case_id": case.case_id,
        "kind": "expertise",
        "selected": sorted(got),
        "expected": sorted(expected),
        "passed": got == expected,
        "loaded_bytes": selection.loaded_bytes,
        "catalog_bytes": selection.catalog_bytes,
    }


def _roles(case: SelectiveCase, repo_root: Path, workdir: Path) -> dict[str, Any]:
    from apiforge.application.analyze import analyze_project
    from apiforge.runtime.economy import load_economy_config
    from apiforge.runtime.role_context import plan_roles

    raw = case.raw
    root = workdir / case.case_id
    shutil.copytree(repo_root / str(raw["fixture"]), root / "proj", ignore=_IGNORED)
    shutil.copyfile(repo_root / str(raw["contract"]), root / "openapi.yaml")
    analyze_project(root / "openapi.yaml", root / "proj", None, root / ".apiforge" / "case")
    profile = str(raw.get("profile", "balanced"))
    context_bytes = int(load_economy_config()["profiles"][profile]["context_bytes"])
    spec = SimpleNamespace(inputs=(f"target={raw['target']}",), outcome=str(raw["outcome"]))
    roles = tuple((str(item["capability"]), str(item["kind"])) for item in raw["roles"])
    plan = plan_roles(root, spec, roles, context_bytes=context_bytes, run_id=f"eval-{case.case_id}")
    by_kind = {row.capability: row for row in plan.roles}
    primary = by_kind[roles[0][0]].bytes
    subordinate_ok = all(row.bytes <= primary for row in plan.roles if row.role != "specialist")
    ratio = round(plan.total_bytes / plan.naive_bytes, 4) if plan.naive_bytes else 1.0
    limit = float(raw.get("max_total_ratio", 0.6))
    return {
        "case_id": case.case_id,
        "kind": "roles",
        "profile": profile,
        "bytes_by_role": {row.capability: row.bytes for row in plan.roles},
        "total_bytes": plan.total_bytes,
        "naive_bytes": plan.naive_bytes,
        "ratio": ratio,
        "unresolved": list(plan.unresolved),
        "passed": bool(plan.capsule_id) and subordinate_ok and ratio <= limit and primary > 0,
    }


def _debate(case: SelectiveCase, workdir: Path) -> dict[str, Any]:
    from apiforge.debate.packet import referee_packet
    from apiforge.debate.service import open_debate, submit

    raw = case.raw
    case_dir = workdir / case.case_id
    debate = open_debate(
        case_dir, str(raw["question"]), tuple(raw["sides"]), "2026-09-28T00:00:00Z"
    )
    cited: set[str] = set()
    for item in raw["submissions"]:
        evidence = tuple(item["evidence"])
        cited.update(evidence)
        submit(
            case_dir,
            debate.debate_id,
            str(item["side"]),
            str(item["position"]),
            evidence,
            disagreements=tuple(
                (str(d["point"]), str(d.get("reason", ""))) for d in item.get("disagreements") or ()
            ),
            risks=tuple(item.get("risks") or ()),
            confidence=item.get("confidence"),
        )
    packet = referee_packet(
        case_dir,
        debate.debate_id,
        capsule_id="ctx://sha256/" + "0" * 64,
        capsule_bytes=int(raw.get("capsule_bytes", 12000)),
    )
    ratio = round(packet.packet_bytes / packet.naive_bytes, 4) if packet.naive_bytes else 1.0
    preserved = cited <= set(packet.evidence)
    return {
        "case_id": case.case_id,
        "kind": "debate",
        "packet_bytes": packet.packet_bytes,
        "naive_bytes": packet.naive_bytes,
        "ratio": ratio,
        "evidence_preserved": preserved,
        "disagreements": list(packet.disagreements),
        "passed": preserved and ratio <= float(raw.get("max_packet_ratio", 0.5)),
    }


def _shadow_rates() -> dict[str, dict[str, float]]:
    from apiforge.runtime.economy import load_economy_config
    from apiforge.runtime.shadow import sample_rate

    ids = [f"run-{index:05d}" for index in range(SHADOW_SAMPLES)]
    rates = {}
    for name, row in sorted(load_economy_config()["profiles"].items()):
        share = float(row.get("shadow_share", 0.0))
        rates[name] = {"share": share, "rate": round(sample_rate(ids, share), 4)}
    return rates


def run_selective_eval(corpus: Path, repo_root: Path) -> dict[str, Any]:
    from apiforge.agentops.agent_audit import audit_agents

    cases = load_corpus(corpus)
    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="af-selective-") as tmp:
        for case in cases:
            if case.kind == "expertise":
                rows.append(_expertise(case))
            elif case.kind == "roles":
                rows.append(_roles(case, Path(repo_root), Path(tmp)))
            else:
                rows.append(_debate(case, Path(tmp)))
    shadow = _shadow_rates()
    first = audit_agents(Path(repo_root))
    second = audit_agents(Path(repo_root))
    gates = {
        "expertise_exact": all(r["passed"] for r in rows if r["kind"] == "expertise"),
        "no_trigger_loads_nothing": any(
            r["kind"] == "expertise" and not r["expected"] and not r["selected"] for r in rows
        ),
        "role_context": all(r["passed"] for r in rows if r["kind"] == "roles"),
        "referee_packet": all(r["passed"] for r in rows if r["kind"] == "debate"),
        "shadow_share": all(
            abs(item["rate"] - item["share"]) <= SHADOW_TOLERANCE for item in shadow.values()
        ),
        "agent_audit_deterministic": first == second and first["agents"] == len(first["rows"]),
    }
    return {
        "schema": "apiforge/selective-eval/v1",
        "cases": len(rows),
        "gates": gates,
        "passed": all(gates.values()),
        "shadow": shadow,
        "agent_audit": {
            "agents": first["agents"],
            "keep": first["keep"],
            "merge_candidates": len(first["merge_candidates"]),
        },
        "rows": rows,
        "tokens": "unresolved",
    }


__all__ = ["SelectiveCase", "load_corpus", "run_selective_eval"]
