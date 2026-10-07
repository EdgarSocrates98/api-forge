"""Append-only hierarchical budget governor.

This module is deliberately provider-free. It admits a measured spend only
after checking every matching task/phase/role/tool limit. Unknown token counts
remain unresolved instead of being estimated from bytes or model metadata.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from apiforge.contracts.agentic_governance import (
    AgenticBudgetPlan,
    BudgetDecision,
    BudgetLimit,
    BudgetSpend,
)
from apiforge.contracts.economy import CostVector
from apiforge.core.models import JsonValue

_DIR = Path(".apiforge") / "economy" / "agentic-budget"
_PLANS = "plans.jsonl"
_SPENDS = "spends.jsonl"


def _directory(root: Path) -> Path:
    resolved = Path(root).resolve()
    if resolved.name == ".apiforge":
        resolved = resolved.parent
    return resolved / _DIR


def _append(directory: Path, filename: str, value: object) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    payload = value.model_dump(mode="json") if hasattr(value, "model_dump") else value
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")
    return path


def _read(directory: Path, filename: str, model: type[Any]) -> list[Any]:
    path = directory / filename
    if not path.is_file():
        return []
    rows: list[Any] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(model.model_validate(json.loads(line)))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"AF-BUDGET-STORE-CORRUPT: {path}:{line_no}: {exc}") from exc
    return rows


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_plan(
    *,
    task_id: str,
    limits: tuple[BudgetLimit, ...],
    created_at: str,
    metadata: dict[str, object] | None = None,
) -> AgenticBudgetPlan:
    """Create a deterministic plan id and content hash from declared limits."""
    body = {
        "task_id": task_id,
        "limits": [item.model_dump(mode="json") for item in limits],
        "metadata": metadata or {},
        "created_at": created_at,
    }
    digest = _digest(body)
    return AgenticBudgetPlan(
        plan_id=f"budget-plan:{digest[:16]}",
        task_id=task_id,
        limits=limits,
        created_at=created_at,
        metadata=cast(dict[str, JsonValue], metadata or {}),
        content_sha256=digest,
    )


def persist_plan(root: Path, plan: AgenticBudgetPlan) -> dict[str, object]:
    """Append a plan once; conflicting ids are refused."""
    directory = _directory(root)
    plans = _read(directory, _PLANS, AgenticBudgetPlan)
    for existing in plans:
        if existing.plan_id == plan.plan_id:
            if existing.content_sha256 != plan.content_sha256:
                raise ValueError(
                    "AF-BUDGET-PLAN-CONFLICT: plan_id already maps to a different content hash"
                )
            return {"status": "deduplicated", "plan": existing.model_dump(mode="json")}
    _append(directory, _PLANS, plan)
    return {"status": "accepted", "plan": plan.model_dump(mode="json")}


def load_plan(root: Path, plan_id: str) -> AgenticBudgetPlan:
    plans = _read(_directory(root), _PLANS, AgenticBudgetPlan)
    for plan in reversed(plans):
        if plan.plan_id == plan_id:
            return cast(AgenticBudgetPlan, plan)
    raise ValueError(
        f"AF-BUDGET-PLAN-NOT-FOUND: {plan_id}; unlock=register an AgenticBudgetPlan first"
    )


def _matches(limit: BudgetLimit, spend: BudgetSpend, task_id: str) -> bool:
    return {
        "task": spend.task_id == task_id and limit.scope_id == task_id,
        "phase": spend.phase == limit.scope_id,
        "role": spend.role == limit.scope_id,
        "tool": spend.tool == limit.scope_id,
    }[limit.scope]


def _total(
    spends: list[BudgetSpend], limit: BudgetLimit, task_id: str, dimension: str
) -> int | None:
    matching = [item for item in spends if _matches(limit, item, task_id)]
    if dimension == "calls":
        return len(matching)
    if dimension == "observed_tokens":
        tokens = [item.cost.observed_tokens for item in matching]
        return (
            None if any(value is None for value in tokens) else sum(value or 0 for value in tokens)
        )
    return sum(int(getattr(item.cost, dimension)) for item in matching)


def check_budget(
    root: Path,
    plan: AgenticBudgetPlan,
    *,
    task_id: str,
    phase: str,
    role: str,
    tool: str,
    cost: CostVector,
    spend_id: str,
) -> BudgetDecision:
    """Evaluate a proposed spend without appending it."""
    if task_id != plan.task_id:
        return BudgetDecision(
            action="unresolved",
            plan_id=plan.plan_id,
            task_id=task_id,
            spend_id=spend_id,
            code="AF-BUDGET-TASK-MISMATCH",
            field="task_id",
            unlock="use the plan task_id for the spend",
            reason="spend task differs from plan",
        )
    spends = [
        item
        for item in _read(_directory(root), _SPENDS, BudgetSpend)
        if item.plan_id == plan.plan_id and item.task_id == task_id
    ]
    exhausted: list[str] = []
    unresolved: list[str] = []
    remaining: dict[str, int | None] = {}
    proposed_values: dict[str, int | None] = {
        "calls": 1,
        "context_bytes": cost.context_bytes,
        "tool_result_bytes": cost.tool_result_bytes,
        "expansions": cost.expansions,
        "duration_ms": cost.duration_ms,
        "observed_tokens": cost.observed_tokens,
    }
    for limit in plan.limits:
        dimensions = {
            "calls": limit.max_calls,
            "context_bytes": limit.max_context_bytes,
            "tool_result_bytes": limit.max_tool_result_bytes,
            "expansions": limit.max_expansions,
            "duration_ms": limit.max_duration_ms,
            "observed_tokens": limit.max_observed_tokens,
        }
        if not _matches(
            limit,
            BudgetSpend(
                spend_id=spend_id,
                plan_id=plan.plan_id,
                task_id=task_id,
                phase=phase,
                role=role,
                tool=tool,
                cost=cost,
                observed_at="governor-check",
            ),
            task_id,
        ):
            continue
        for dimension, maximum in dimensions.items():
            if maximum is None:
                continue
            current = _total(spends, limit, task_id, dimension)
            proposed = proposed_values[dimension]
            key = f"{limit.scope_id}.{dimension}"
            if dimension == "observed_tokens" and (current is None or proposed is None):
                unresolved.append(key)
                remaining[key] = None
                continue
            total = int(current or 0) + int(proposed or 0)
            remaining[key] = maximum - total
            if total > maximum:
                exhausted.append(key)
    if unresolved:
        return BudgetDecision(
            action="unresolved",
            plan_id=plan.plan_id,
            task_id=task_id,
            spend_id=spend_id,
            code="AF-BUDGET-TOKENS-UNRESOLVED",
            field="cost.observed_tokens",
            unlock="supply an observed token receipt before enforcing token limits",
            reason="token budget cannot be estimated from bytes",
            unresolved=tuple(unresolved),
            remaining=remaining,
        )
    if exhausted:
        return BudgetDecision(
            action="stop",
            plan_id=plan.plan_id,
            task_id=task_id,
            spend_id=spend_id,
            code="AF-BUDGET-EXHAUSTED",
            field="limits",
            unlock="reduce the requested spend or obtain an explicitly reviewed new plan",
            reason="one or more hierarchical limits would be exceeded",
            exhausted=tuple(exhausted),
            remaining=remaining,
        )
    return BudgetDecision(
        action="allow",
        plan_id=plan.plan_id,
        task_id=task_id,
        spend_id=spend_id,
        reason="all matching hierarchical limits remain within budget",
        remaining=remaining,
    )


def record_spend(root: Path, plan: AgenticBudgetPlan, spend: BudgetSpend) -> BudgetDecision:
    """Check and append a spend only when admission is explicitly allowed."""
    if spend.plan_id != plan.plan_id or spend.task_id != plan.task_id:
        return BudgetDecision(
            action="unresolved",
            plan_id=plan.plan_id,
            task_id=spend.task_id,
            spend_id=spend.spend_id,
            code="AF-BUDGET-TASK-MISMATCH",
            field="plan_id/task_id",
            unlock="use a spend bound to the loaded plan",
            reason="spend is outside plan scope",
        )
    existing = _read(_directory(root), _SPENDS, BudgetSpend)
    if any(item.spend_id == spend.spend_id for item in existing):
        return BudgetDecision(
            action="deduplicated",
            plan_id=plan.plan_id,
            task_id=spend.task_id,
            spend_id=spend.spend_id,
            reason="spend receipt already exists",
        )
    decision = check_budget(
        root,
        plan,
        task_id=spend.task_id,
        phase=spend.phase,
        role=spend.role,
        tool=spend.tool,
        cost=spend.cost,
        spend_id=spend.spend_id,
    )
    if decision.action != "allow":
        return decision
    _append(_directory(root), _SPENDS, spend)
    return decision.model_copy(update={"recorded": True})


__all__ = ["build_plan", "check_budget", "load_plan", "persist_plan", "record_spend"]
