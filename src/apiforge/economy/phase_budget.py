"""Per-SDD-phase budgets (§104): split the profile envelope over the SDD chain.

Calls are allocated by largest remainder so they sum to the envelope; a
protected phase (contract, verify, secure — §100) always gets at least one
call and an overrun there is ``protected_overrun``: reported, never cut. A
non-protected overrun is ``exceeded`` and leaves the plan ``unresolved``.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_resume import PhaseBudget, PhaseBudgetPlan
from apiforge.runtime.economy import envelope_for, load_economy_config, validate_profile

PHASES_FILE = Path(__file__).resolve().parents[1] / "rules" / "phase_budgets.yaml"


def _refusal(code: str, detail: str, field: str, unlock: str) -> ContractError:
    error = ContractError(code, detail)
    error.field = field  # type: ignore[attr-defined]
    error.unlock = unlock  # type: ignore[attr-defined]
    return error


def load_phases(path: Path = PHASES_FILE) -> list[dict[str, Any]]:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise _refusal(
            "AF-BUDGET-PHASE-POLICY", f"{path}: {exc}", "rules", "restore rules/phase_budgets.yaml"
        ) from exc
    phases = raw.get("phases")
    if (
        not isinstance(phases, list)
        or not phases
        or not all(
            isinstance(item, dict) and "phase" in item and "share" in item for item in phases
        )
        or abs(sum(float(item["share"]) for item in phases) - 1.0) > 1e-6
    ):
        raise _refusal(
            "AF-BUDGET-PHASE-POLICY",
            f"{path}: phases must be a list of {{phase, share}} whose shares sum to 1.0",
            "rules",
            "restore rules/phase_budgets.yaml",
        )
    return phases


def _allocate(total: int, shares: list[float], floors: list[int]) -> list[int]:
    """Reserve protected floors first, then split the rest by largest remainder."""
    rest = max(0, total - sum(floors))
    raw = [rest * share for share in shares]
    calls = [math.floor(value) for value in raw]
    order = sorted(range(len(raw)), key=lambda index: (calls[index] - raw[index], index))
    for index in order[: rest - sum(calls)]:
        calls[index] += 1
    return [value + floor for value, floor in zip(calls, floors, strict=True)]


def load_usage(path: Path) -> dict[str, dict[str, int]]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise TypeError("usage must be an object keyed by phase")
        return {
            str(phase): {key: int(value) for key, value in dict(row).items()}
            for phase, row in data.items()
        }
    except (OSError, ValueError, TypeError) as exc:
        raise _refusal(
            "AF-BUDGET-PHASE-USAGE",
            f"{path}: {exc}",
            "usage",
            'pass {"<phase>": {"calls": n, "context_bytes": n}}',
        ) from exc


def plan_phase_budgets(
    profile: str, *, usage: dict[str, dict[str, int]] | None = None
) -> PhaseBudgetPlan:
    effective = validate_profile(profile) or "balanced"
    envelope = envelope_for(effective, load_economy_config())
    phases = load_phases()
    names = [str(item["phase"]) for item in phases]
    unknown = sorted(set(usage or {}) - set(names))
    if unknown:
        raise _refusal(
            "AF-BUDGET-PHASE-UNKNOWN",
            f"usage names unknown phase(s): {', '.join(unknown)}",
            "usage",
            f"use SDD phases: {', '.join(names)}",
        )
    protected = [bool(item.get("protected", False)) for item in phases]
    shares = [float(item["share"]) for item in phases]
    calls = _allocate(envelope.provider_calls, shares, [1 if flag else 0 for flag in protected])
    rows: list[PhaseBudget] = []
    codes: set[str] = set()
    for name, share, budget_calls, is_protected in zip(
        names, shares, calls, protected, strict=True
    ):
        context = int(envelope.context_bytes * share)
        used = (usage or {}).get(name)
        status = "unmeasured"
        if used is not None:
            over = used.get("calls", 0) > budget_calls or used.get("context_bytes", 0) > context
            if over and is_protected:
                status = "protected_overrun"
                codes.add("AF-BUDGET-PHASE-PROTECTED")
            elif over:
                status = "exceeded"
                codes.add("AF-BUDGET-PHASE-EXCEEDED")
            else:
                status = "within"
        rows.append(
            PhaseBudget(
                phase=name,
                share=share,
                calls=budget_calls,
                context_bytes=context,
                protected=is_protected,
                used_calls=used.get("calls") if used else None,
                used_context_bytes=used.get("context_bytes") if used else None,
                status=status,  # type: ignore[arg-type]
            )
        )
    return PhaseBudgetPlan(
        profile=effective,
        total_calls=envelope.provider_calls,
        total_context_bytes=envelope.context_bytes,
        phases=tuple(rows),
        status="unresolved" if "AF-BUDGET-PHASE-EXCEEDED" in codes else "ok",
        codes=tuple(sorted(codes)),
    )


__all__ = ["load_phases", "load_usage", "plan_phase_budgets"]
