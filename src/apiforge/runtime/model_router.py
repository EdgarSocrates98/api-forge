"""§33 Adaptive Model Router — model routing kept separate from
capability/agent routing. Pure function over declared inputs, declared
candidate descriptors and §34 scorecards. Quality history below the floor
makes a candidate ineligible; missing signals land in ``unresolved``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.model_routing import (
    ModelCandidate,
    ModelRouteDecision,
    ModelRouteInputs,
    ModelScorecard,
    ModelTaskClass,
    RankedModel,
)
from apiforge.economy.run_ledger import EconomyError
from apiforge.governance.control_plane import evaluate_route

RULES = Path(__file__).resolve().parent.parent / "rules" / "model_router.yaml"

NO_ELIGIBLE_MODEL = "AF-ROUTE-NO-ELIGIBLE-MODEL"
ROUTER_POLICY_INVALID = "AF-ROUTE-POLICY-INVALID"

_REASON_TIER = {"none": 0, "light": 1, "deep": 2}
_COMPLEXITY_REASON = {None: 0, "micro": 0, "low": 0, "medium": 1, "high": 2}


def load_model_router_policy(path: Path | None = None) -> dict[str, Any]:
    data = yaml.safe_load((path or RULES).read_text(encoding="utf-8")) or {}
    if data.get("version") != 1:
        raise EconomyError(
            ROUTER_POLICY_INVALID,
            f"{path or RULES}: expected version 1",
            field="version",
            unlock="align the router policy schema",
        )
    return {
        "quality_floor": float(data.get("quality_floor", 0.8)),
        "min_evaluations": int(data.get("min_evaluations", 3)),
        "weights": {
            "quality": float((data.get("weights") or {}).get("quality", 0.45)),
            "latency": float((data.get("weights") or {}).get("latency", 0.15)),
            "cost": float((data.get("weights") or {}).get("cost", 0.25)),
            "availability": float((data.get("weights") or {}).get("availability", 0.15)),
        },
        "candidates": tuple(
            ModelCandidate.model_validate(row) for row in data.get("candidates") or ()
        ),
    }


def _scorecard_key(candidate: ModelCandidate) -> tuple[str, str]:
    return candidate.provider, candidate.model


def _scorecard_for(
    candidate: ModelCandidate,
    inputs: ModelRouteInputs,
    scorecards: dict[tuple[str, str], ModelScorecard]
    | dict[tuple[str, str, ModelTaskClass], ModelScorecard],
) -> ModelScorecard | None:
    if inputs.task_class is not None:
        keyed = scorecards.get((candidate.provider, candidate.model, inputs.task_class))  # type: ignore[arg-type]
        if keyed is not None:
            return keyed
    card = scorecards.get(_scorecard_key(candidate))  # type: ignore[arg-type]
    if card is not None and inputs.task_class is not None and card.task_class != inputs.task_class:
        return None
    return card


def _constraints(candidate: ModelCandidate, inputs: ModelRouteInputs) -> list[str]:
    """Hard requirements — a missing one makes the candidate ineligible."""
    reasons: list[str] = []
    if inputs.needs_tool_support and not candidate.tool_support:
        reasons.append("tool-support-required")
    if inputs.needs_structured_output and not candidate.structured_output:
        reasons.append("structured-output-required")
    needed_reason = _COMPLEXITY_REASON.get(inputs.task_complexity, 0)
    if inputs.reasoning_needs is not None:
        needed_reason = max(needed_reason, _REASON_TIER[inputs.reasoning_needs])
    if _REASON_TIER[candidate.reasoning_tier] < needed_reason:
        reasons.append("reasoning-tier-insufficient")
    if (
        inputs.context_size is not None
        and candidate.context_window
        and candidate.context_window < inputs.context_size
    ):
        reasons.append("context-window-too-small")
    if (
        inputs.max_latency_ms is not None
        and candidate.latency_p50_ms is not None
        and candidate.latency_p50_ms > inputs.max_latency_ms
    ):
        reasons.append("latency-over-max")
    if (
        inputs.max_cost is not None
        and candidate.cost_per_1k is not None
        and candidate.cost_per_1k > inputs.max_cost
    ):
        reasons.append("cost-over-max")
    calls_left = inputs.budget_remaining.get("calls")
    if isinstance(calls_left, (int, float)) and calls_left <= 0:
        reasons.append("budget-calls-exhausted")
    budget_latency = inputs.budget_remaining.get("latency_ms")
    if (
        isinstance(budget_latency, (int, float))
        and candidate.latency_p50_ms is not None
        and candidate.latency_p50_ms > budget_latency
    ):
        reasons.append("latency-over-budget")
    budget_cost = inputs.budget_remaining.get("cost")
    if (
        isinstance(budget_cost, (int, float))
        and candidate.cost_per_1k is not None
        and candidate.cost_per_1k > budget_cost
    ):
        reasons.append("cost-over-budget")
    if candidate.availability == "unavailable":
        reasons.append("availability-unavailable")
    return reasons


def _normalize(value: float | None, cap: float) -> float | None:
    if value is None or cap <= 0:
        return None
    return max(0.0, 1.0 - (value / cap))


def route_model(
    inputs: ModelRouteInputs,
    candidates: tuple[ModelCandidate, ...],
    scorecards: dict[tuple[str, str], ModelScorecard]
    | dict[tuple[str, str, ModelTaskClass], ModelScorecard]
    | None = None,
    *,
    policy: dict[str, Any] | None = None,
) -> ModelRouteDecision:
    """Rank eligible models; quality evidence is a constraint, not a guess."""
    rules = policy or load_model_router_policy()
    unresolved: list[str] = []
    for name, value in (
        ("task_complexity", inputs.task_complexity),
        ("task_class", inputs.task_class),
        ("risk", inputs.risk),
        ("reasoning_needs", inputs.reasoning_needs),
        ("context_size", inputs.context_size),
    ):
        if value is None:
            unresolved.append(name)
    weights = rules["weights"]
    floor = rules["quality_floor"]
    cards = scorecards or {}
    ranked: list[RankedModel] = []
    for candidate in candidates:
        reasons = _constraints(candidate, inputs)
        card = _scorecard_for(candidate, inputs, cards)
        if card is not None and card.freshness_state in {
            "stale",
            "degraded",
            "unresolved",
            "conflicted",
            "deprecated",
        }:
            reasons.append(f"scorecard-{card.freshness_state}")
        if (
            card is not None
            and card.freshness_state in {"cold", "warming"}
            and inputs.risk
            in {
                "sensitive",
                "external_mutation",
                "destructive",
                "irreversible",
            }
        ):
            reasons.append("scorecard-not-mature-for-risk")
        if inputs.risk in {
            "sensitive",
            "external_mutation",
            "destructive",
            "irreversible",
        }:
            if card is None:
                unresolved.append("scorecard")
            elif card.evidence_correctness is None:
                reasons.append("evidence-correctness-unresolved")
        if card is not None and card.evaluation_count < rules["min_evaluations"]:
            reasons.append("insufficient-evaluations")
        if (
            card is not None
            and card.quality is not None
            and card.evaluation_count >= rules["min_evaluations"]
            and card.quality < floor
        ):
            reasons.append("quality-below-floor")
        if reasons:
            ranked.append(
                RankedModel(
                    provider=candidate.provider,
                    model=candidate.model,
                    eligible=False,
                    reasons=tuple(reasons),
                )
            )
            continue
        latency_cap = inputs.max_latency_ms or 60_000
        cost_cap = inputs.max_cost or 10.0
        latency_score = _normalize(
            card.latency_p50_ms if card else candidate.latency_p50_ms, latency_cap
        )
        cost_score = _normalize(card.cost_mean if card else candidate.cost_per_1k, cost_cap)
        availability_score = {
            "available": 1.0,
            "degraded": 0.5,
            "unknown": None,
            "unavailable": 0.0,
        }[candidate.availability]
        quality_score = card.quality if card else None
        terms = [
            (weights["quality"], quality_score),
            (weights["latency"], latency_score),
            (weights["cost"], cost_score),
            (weights["availability"], availability_score),
        ]
        present = [(w, v) for w, v in terms if v is not None]
        score = sum(w * v for w, v in present) / sum(w for w, _ in present) if present else None
        ranked.append(
            RankedModel(
                provider=candidate.provider,
                model=candidate.model,
                eligible=True,
                score=round(score, 4) if score is not None else None,
                reasons=() if card else ("scorecard-missing",),
            )
        )
    eligible = [item for item in ranked if item.eligible]
    role_order = {"champion": 2, "fallback": 1, "challenger": 0}
    eligible = [
        item
        for item in eligible
        if inputs.allow_challenger
        or next(
            (
                candidate.role != "challenger"
                for candidate in candidates
                if candidate.provider == item.provider and candidate.model == item.model
            ),
            True,
        )
    ]
    eligible.sort(
        key=lambda item: (
            role_order.get(
                next(
                    (
                        candidate.role
                        for candidate in candidates
                        if candidate.provider == item.provider and candidate.model == item.model
                    ),
                    "fallback",
                ),
                1,
            ),
            item.score or 0.0,
            item.model,
        ),
        reverse=True,
    )
    selected = f"{eligible[0].provider}/{eligible[0].model}" if eligible else None
    return ModelRouteDecision(
        selected=selected,
        ranked=tuple(ranked),
        code=None if selected else NO_ELIGIBLE_MODEL,
        reason=(
            f"{len(eligible)} eligible of {len(ranked)} candidates"
            if selected
            else "no candidate survived the declared constraints"
        ),
        unresolved=tuple(sorted(unresolved)),
    )


def route_model_shadow(
    root: Path,
    inputs: ModelRouteInputs,
    candidates: tuple[ModelCandidate, ...],
    scorecards: dict[tuple[str, str], ModelScorecard]
    | dict[tuple[str, str, ModelTaskClass], ModelScorecard]
    | None = None,
    *,
    legacy_decision: dict[str, object] | None = None,
    policy: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, object]:
    """Run model routing as a non-authoritative Decision Plane shadow."""
    candidate = route_model(inputs, candidates, scorecards, policy=policy)
    eligible = [item for item in candidate.ranked if item.eligible]
    control = evaluate_route(
        root,
        "model_routing",
        candidate_decision=candidate.model_dump(mode="json"),
        legacy_decision=legacy_decision or {},
        confidence=eligible[0].score if eligible else None,
        evidence_refs=("model-route-inputs",),
        now=now or datetime.now(UTC),
    )
    return {
        "candidate": candidate.model_dump(mode="json"),
        "control": control.model_dump(mode="json"),
    }


__all__ = [
    "NO_ELIGIBLE_MODEL",
    "ROUTER_POLICY_INVALID",
    "load_model_router_policy",
    "route_model",
    "route_model_shadow",
]
