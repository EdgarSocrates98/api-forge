"""§24 memory evals: a corpus over the eight declared axes — usefulness,
poisoning, staleness, wrong-environment reuse, conflicting memory,
cross-task leakage, retrieval and invalidation.

Each case drives the real governed store on an isolated root: setup
seeds records through ``persist_candidate`` (the only honest ingress),
the action queries, persists or plans invalidation, and the expectation
is checked against the observed contract — never against a narration.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.agentic_memory import (
    MemoryCandidate,
    MemoryPolicy,
    MemoryQuery,
    MemoryRecord,
)
from apiforge.contracts.base import ContractError
from apiforge.contracts.eval_plane import MemoryEvalCaseResult, MemoryEvalReport
from apiforge.memory import store as memory_store
from apiforge.memory.invalidation import suggest_invalidations
from apiforge.memory.retrieval import query_memory_scored

NOW = "2026-10-06T00:00:00+00:00"

AXES = {
    "memory_usefulness",
    "memory_poisoning",
    "stale_memory",
    "wrong_environment_reuse",
    "conflicting_memory",
    "cross_task_leakage",
    "memory_retrieval",
    "memory_invalidation",
}


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError("AF-EVALS-INVALID", f"memory-evals corpus {corpus} empty or duplicated")
    for case in cases:
        if str(case.get("axis")) not in AXES:
            raise ContractError(
                "AF-EVALS-INVALID",
                f"{case.get('id')}: axis {case.get('axis')!r} not in {sorted(AXES)}",
            )
    return cases


def _record(raw: dict[str, Any], index: int) -> MemoryRecord:
    raw = dict(raw)
    return MemoryRecord(
        memory_id=str(raw.pop("memory_id", f"memory:{index:016x}")),
        content_sha256=str(raw.pop("content_sha256", f"{index:064x}")),
        created_at=str(raw.pop("created_at", NOW)),
        **raw,
    )


def _candidate(raw: dict[str, Any], index: int) -> MemoryCandidate:
    raw = dict(raw)
    return MemoryCandidate(
        candidate_id=str(raw.pop("candidate_id", f"candidate:{index:016x}")),
        record=_record(raw.pop("record") or {}, index),
        proposed_by=str(raw.pop("proposed_by", "eval")),
        reason=str(raw.pop("reason", "memory eval")),
        unresolved=tuple(raw.pop("unresolved", ()) or ()),
    )


def _policy(raw: dict[str, Any] | None) -> MemoryPolicy:
    raw = dict(raw or {})
    return MemoryPolicy(policy_id=str(raw.pop("policy_id", "eval-policy")), **raw)


def _setup(root: Path, case: dict[str, Any]) -> MemoryPolicy:
    policy = _policy((case.get("setup") or {}).get("policy"))
    for index, raw in enumerate((case.get("setup") or {}).get("records") or ()):
        memory_store.persist_candidate(root, _candidate({"record": raw}, index), policy, now=NOW)
    return policy


def _act_persist(root: Path, policy: MemoryPolicy, action: dict[str, Any]) -> dict[str, Any]:
    outcome = memory_store.persist_candidate(
        root, _candidate(action.get("candidate") or {}, 100), policy, now=NOW
    )
    return {
        "kind": "outcome",
        "action": str(outcome.action),
        "accepted": outcome.accepted,
        "code": outcome.code or "",
        "reason": outcome.reason,
    }


def _act_query(root: Path, _policy: MemoryPolicy, action: dict[str, Any]) -> dict[str, Any]:
    raw = dict(action.get("query") or {})
    raw.setdefault("now", NOW)
    if action.get("scored"):
        query = MemoryQuery(**raw)
        ranked = query_memory_scored(root, query)
        return {
            "kind": "ranked",
            "memory_ids": [row.memory_id for row in ranked.ranked],
            "scores": [row.score for row in ranked.ranked],
            "unresolved": list(ranked.unresolved),
        }
    result = memory_store.query_memory(root, MemoryQuery(**raw))
    return {
        "kind": "result",
        "memory_ids": [record.memory_id for record in result.records],
        "stale_count": result.stale_count,
        "invalidated_count": result.invalidated_count,
        "status": str(result.status),
        "unresolved": list(result.unresolved),
    }


def _act_suggest(root: Path, _policy: MemoryPolicy, action: dict[str, Any]) -> dict[str, Any]:
    plan = suggest_invalidations(
        root,
        str(action.get("trigger", "runtime_change")),  # type: ignore[arg-type]
        environment_fingerprint=action.get("environment_fingerprint"),
        changed=tuple(action.get("changed") or ()),
        memory_ids=tuple(action.get("memory_ids") or ()),
    )
    return {
        "kind": "plan",
        "memory_ids": list(plan.memory_ids),
        "unresolved": list(plan.unresolved),
    }


def _act_quarantine(root: Path, _policy: MemoryPolicy, _action: dict[str, Any]) -> dict[str, Any]:
    rows = memory_store.list_quarantine(root)
    return {
        "kind": "quarantine",
        "memory_ids": [row.memory_id for row in rows],
        "count": len(rows),
    }


_ACTIONS = {
    "persist_candidate": _act_persist,
    "query": _act_query,
    "invalidate_suggest": _act_suggest,
    "quarantine_list": _act_quarantine,
}


def _check(case: dict[str, Any], observed: dict[str, Any]) -> list[str]:
    expect = case.get("expect") or {}
    problems: list[str] = []
    if expect.get("action") and observed.get("action") != expect["action"]:
        problems.append(f"action {observed.get('action')} != {expect['action']}")
    if "accepted" in expect and observed.get("accepted") != bool(expect["accepted"]):
        problems.append(f"accepted {observed.get('accepted')} != {expect['accepted']}")
    if expect.get("code") and expect["code"] not in str(observed.get("code", "")):
        problems.append(f"code {observed.get('code')} lacks {expect['code']}")
    if "status" in expect and observed.get("status") != expect["status"]:
        problems.append(f"status {observed.get('status')} != {expect['status']}")
    present = set(observed.get("memory_ids") or ())
    for memory_id in expect.get("memory_ids") or ():
        if memory_id not in present:
            problems.append(f"memory {memory_id} absent")
    for memory_id in expect.get("absent_ids") or ():
        if memory_id in present:
            problems.append(f"memory {memory_id} leaked")
    if "count" in expect:
        actual = observed.get("count", len(observed.get("memory_ids") or ()))
        if actual != int(expect["count"]):
            problems.append(f"count {actual} != {expect['count']}")
    if "min_score" in expect:
        scores = observed.get("scores") or []
        if not scores or max(scores) < float(expect["min_score"]):
            problems.append(f"top score {scores[:1]} < {expect['min_score']}")
    for fragment in expect.get("unresolved_contains") or ():
        if not any(fragment in entry for entry in observed.get("unresolved") or ()):
            problems.append(f"unresolved lacks {fragment!r}")
    return problems


def _run_case(case: dict[str, Any], root: Path) -> MemoryEvalCaseResult:
    policy = _setup(root, case)
    action = dict(case.get("action") or {})
    runner = _ACTIONS.get(str(action.get("type")))
    if runner is None:
        return MemoryEvalCaseResult(
            case_id=str(case["id"]),
            axis=str(case["axis"]),
            expected=str(case.get("expect", {})),
            observed="no action",
            passed=False,
            detail=f"unknown action {action.get('type')!r}",
        )
    observed = runner(root, policy, action)
    problems = _check(case, observed)
    return MemoryEvalCaseResult(
        case_id=str(case["id"]),
        axis=str(case["axis"]),
        expected=str(case.get("expect") or {}),
        observed=f"{observed.get('kind')}:{observed.get('action', observed.get('status', 'ok'))}",
        passed=not problems,
        detail="; ".join(problems),
    )


def run_memory_evals(corpus: Path) -> dict[str, Any]:
    cases = load_cases(corpus)
    results: list[MemoryEvalCaseResult] = []
    for case in cases:
        with tempfile.TemporaryDirectory(prefix="af-memory-eval-") as tmp:
            results.append(_run_case(case, Path(tmp)))
    report = MemoryEvalReport(
        cases=tuple(results),
        totals={
            "cases": len(results),
            "passed": sum(1 for result in results if result.passed),
        },
    )
    failed = [result.case_id for result in results if not result.passed]
    return {
        "schema": "apiforge/memory-evals/v1",
        "corpus": str(corpus),
        "report": report.model_dump(mode="json"),
        "cases": [
            {"id": r.case_id, "axis": r.axis, "passed": r.passed, "detail": r.detail}
            for r in results
        ],
        "totals": {**report.totals, "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["load_cases", "run_memory_evals"]
