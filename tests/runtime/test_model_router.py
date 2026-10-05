"""§33-§35 model router, scorecard and promotion-evidence tests."""

from __future__ import annotations

import pytest

from apiforge.contracts.model_routing import (
    ModelCandidate,
    ModelEvaluation,
    ModelRouteInputs,
)
from apiforge.runtime.model_router import load_model_router_policy, route_model
from apiforge.runtime.model_scorecard import aggregate_scorecards, scorecard_map


def _candidates() -> tuple[ModelCandidate, ...]:
    return (
        ModelCandidate(
            provider="local",
            model="small",
            tool_support=False,
            structured_output=True,
            context_window=32000,
            reasoning_tier="none",
            availability="available",
            cost_per_1k=0.0,
            latency_p50_ms=800,
        ),
        ModelCandidate(
            provider="mid",
            model="mid-v1",
            tool_support=True,
            structured_output=True,
            context_window=200000,
            reasoning_tier="light",
            availability="available",
            cost_per_1k=0.01,
            latency_p50_ms=2500,
        ),
        ModelCandidate(
            provider="top",
            model="top-v1",
            tool_support=True,
            structured_output=True,
            context_window=1000000,
            reasoning_tier="deep",
            availability="available",
            cost_per_1k=0.06,
            latency_p50_ms=9000,
        ),
    )


def test_policy_loads_declared_candidates() -> None:
    rules = load_model_router_policy()
    assert len(rules["candidates"]) == 3
    assert rules["quality_floor"] == 0.8


def test_deep_reasoning_selects_strongest() -> None:
    decision = route_model(
        ModelRouteInputs(
            task_complexity="high",
            reasoning_needs="deep",
            needs_tool_support=True,
            context_size=150000,
        ),
        _candidates(),
    )
    assert decision.selected == "top/top-v1"
    ineligible = {r.model: r.reasons for r in decision.ranked if not r.eligible}
    assert "reasoning-tier-insufficient" in ineligible["mid-v1"]
    assert "context-window-too-small" in ineligible["small"]


def test_unresolved_inputs_named() -> None:
    decision = route_model(ModelRouteInputs(), _candidates())
    assert "task_complexity" in decision.unresolved
    assert "risk" in decision.unresolved


def test_no_eligible_when_all_constrained() -> None:
    decision = route_model(
        ModelRouteInputs(needs_tool_support=True, max_cost=0.001),
        _candidates(),
    )
    # local fails tool_support, mid+top fail cost -> none eligible
    assert decision.selected is None
    assert decision.code == "AF-ROUTE-NO-ELIGIBLE-MODEL"


def test_scorecard_floor_and_freshness() -> None:
    rows = [
        ModelEvaluation(
            provider="mid",
            model="mid-v1",
            task_class="analysis",
            quality=0.5,
            latency_ms=2000,
            cost=0.01,
            recorded_at="2026-10-06T00:00:00Z",
        )
        for _ in range(4)
    ]
    cards = scorecard_map(aggregate_scorecards(rows))
    assert cards[("mid", "mid-v1")].quality == pytest.approx(0.5)
    assert cards[("mid", "mid-v1")].evaluation_count == 4

    decision = route_model(
        ModelRouteInputs(reasoning_needs="light", needs_tool_support=True),
        _candidates(),
        cards,
        policy=load_model_router_policy(),
    )
    mid = next(r for r in decision.ranked if r.model == "mid-v1")
    assert "quality-below-floor" in mid.reasons
    assert not mid.eligible


def test_insufficient_evaluations_blocks_quality_claim() -> None:
    rows = [
        ModelEvaluation(
            provider="mid",
            model="mid-v1",
            task_class="analysis",
            quality=0.99,
            recorded_at="2026-10-06T00:00:00Z",
        )
    ]
    cards = scorecard_map(aggregate_scorecards(rows))
    decision = route_model(
        ModelRouteInputs(reasoning_needs="light", needs_tool_support=True),
        _candidates(),
        cards,
        policy=load_model_router_policy(),
    )
    mid = next(r for r in decision.ranked if r.model == "mid-v1")
    assert "insufficient-evaluations" in mid.reasons


def test_scorecard_unresolved_metrics_named() -> None:
    rows = [
        ModelEvaluation(
            provider="mid",
            model="mid-v1",
            task_class="generation",
            failed=True,
            recorded_at="2026-10-06T00:00:00Z",
        )
    ]
    card = aggregate_scorecards(rows)[("mid", "mid-v1", "generation")]
    assert card.quality is None
    assert "quality" in card.unresolved
    assert card.failure_rate == 1.0


def test_unavailable_candidate_ineligible() -> None:
    candidates = _candidates() + (
        ModelCandidate(
            provider="down",
            model="down-v1",
            tool_support=True,
            structured_output=True,
            context_window=100000,
            reasoning_tier="deep",
            availability="unavailable",
            cost_per_1k=0.01,
            latency_p50_ms=100,
        ),
    )
    decision = route_model(
        ModelRouteInputs(reasoning_needs="deep", needs_tool_support=True), candidates
    )
    down = next(r for r in decision.ranked if r.model == "down-v1")
    assert "availability-unavailable" in down.reasons


def test_budget_and_risk_require_declared_evidence() -> None:
    decision = route_model(
        ModelRouteInputs(
            risk="sensitive",
            needs_tool_support=True,
            budget_remaining={"calls": 0, "cost": 0.001},
        ),
        _candidates(),
    )
    assert decision.selected is None
    assert all("budget-calls-exhausted" in item.reasons for item in decision.ranked)
    assert all("risk-scorecard-required" in item.reasons for item in decision.ranked)


def test_challenger_is_opt_in_and_champion_is_preferred() -> None:
    candidates = (
        ModelCandidate(
            provider="champion",
            model="champion-v1",
            role="champion",
            availability="available",
            structured_output=True,
            cost_per_1k=0.01,
        ),
        ModelCandidate(
            provider="challenger",
            model="challenger-v1",
            role="challenger",
            availability="available",
            structured_output=True,
            cost_per_1k=0.0,
        ),
    )
    default = route_model(ModelRouteInputs(needs_structured_output=True), candidates)
    assert default.selected == "champion/champion-v1"
    enabled = route_model(
        ModelRouteInputs(needs_structured_output=True, allow_challenger=True), candidates
    )
    assert enabled.selected == "champion/champion-v1"
