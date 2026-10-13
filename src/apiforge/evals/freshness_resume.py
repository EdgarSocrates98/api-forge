"""Economy wave 8 eval: freshness watch, live gating, escalation, phase budgets, resume pinning.

Every case is deterministic and offline. The watch case runs over the corpus
``packs/`` directory and its local ``manifest.json``; nothing is fetched.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    rows = [
        yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [str(row.get("id")) for row in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"economy-freshness corpus {corpus} empty or duplicated"
        )
    return rows


def _watch(case: dict[str, Any], corpus: Path) -> dict[str, Any]:
    from apiforge.knowledge.watch import watch_packs

    result = watch_packs(corpus / "manifest.json", now=str(case["now"]), root=corpus / "packs")
    got = {entry.pack_id: entry.state for entry in result.entries}
    expected = {str(key): str(value) for key, value in dict(case["expect"]).items()}
    return {"states": got, "passed": got == expected and result.fetches is False}


def _gate(case: dict[str, Any]) -> dict[str, Any]:
    from apiforge.evidence.live_gate import gate

    try:
        decision = gate(
            str(case["question"]), requested=case.get("mode"), offline=bool(case.get("offline"))
        )
    except ContractError as exc:
        return {"code": exc.code, "passed": exc.code == case.get("expect_code")}
    ok = decision.mode == case["expect_mode"] and decision.live_allowed is case["expect_live"]
    return {"mode": decision.mode, "live_allowed": decision.live_allowed, "passed": ok}


def _escalate(case: dict[str, Any]) -> dict[str, Any]:
    from apiforge.verification.progressive import escalate

    step = escalate(
        static=str(case.get("static", "missing")),
        test=case.get("test"),
        runtime=str(case.get("runtime", "missing")),
    )
    ok = step.action == case["expect_action"] and step.next_mode == case.get("expect_next")
    ok = ok and step.next_mode in {None, "test", "live_read_only"}
    return {"action": step.action, "next_mode": step.next_mode, "passed": ok}


def _phase(case: dict[str, Any]) -> dict[str, Any]:
    from apiforge.economy.phase_budget import plan_phase_budgets

    usage = {str(key): dict(value) for key, value in dict(case.get("usage") or {}).items()}
    plan = plan_phase_budgets(str(case["profile"]), usage=usage)
    statuses = {row.phase: row.status for row in plan.phases}
    ok = plan.status == case["expect_status"]
    ok = ok and all(
        statuses[key] == value for key, value in dict(case.get("expect_phase") or {}).items()
    )
    ok = ok and sum(row.calls for row in plan.phases) == plan.total_calls
    ok = ok and all(row.calls >= 1 for row in plan.phases if row.protected)
    return {"status": plan.status, "codes": list(plan.codes), "passed": ok}


def _checkpoint(case: dict[str, Any]) -> dict[str, Any]:
    from apiforge.contracts.economy_resume import EconomyCheckpoint
    from apiforge.runtime.economy_checkpoint import pin_profile

    checkpoint = EconomyCheckpoint(
        run_id="run-eval",
        task_id="task-eval",
        requested=case["checkpoint_effective"],
        effective=case["checkpoint_effective"],
        max_calls=8,
        calls_used=3,
        calls_remaining=5,
        updated_at="2026-09-28T00:00:00+00:00",
    )
    profile, notes = pin_profile(checkpoint, case.get("requested"))
    codes = sorted({note.split(":", 1)[0] for note in notes})
    ok = profile == case["expect_profile"]
    if case.get("expect_code"):
        ok = ok and case["expect_code"] in codes
    return {"profile": profile, "codes": codes, "passed": ok}


def run_freshness_resume(corpus: Path) -> dict[str, Any]:
    corpus = Path(corpus)
    rows: list[dict[str, Any]] = []
    for case in load_cases(corpus):
        kind = case["kind"]
        if kind == "watch":
            row = _watch(case, corpus)
        elif kind == "gate":
            row = _gate(case)
        elif kind == "escalate":
            row = _escalate(case)
        elif kind == "phase":
            row = _phase(case)
        elif kind == "checkpoint":
            row = _checkpoint(case)
        else:
            raise ContractError("AF-EVALS-INVALID", f"unknown case kind {kind!r}")
        rows.append({"case_id": case["id"], "kind": kind, **row})
    kinds = sorted({row["kind"] for row in rows})
    gates = {kind: all(row["passed"] for row in rows if row["kind"] == kind) for kind in kinds}
    return {
        "schema": "apiforge/economy-freshness-eval/v1",
        "cases": len(rows),
        "gates": gates,
        "passed": all(gates.values()),
        "rows": rows,
    }


__all__ = ["load_cases", "run_freshness_resume"]
