"""Executable Tier-2 local probes for Runtime Convergence Hardening II."""

from __future__ import annotations

from apiforge.contracts.agentic import AgentScorecard
from apiforge.contracts.agentic_memory import MemoryPolicy, MemoryQuery
from apiforge.contracts.routing import CandidateAssessment
from apiforge.contracts.scorecard_routing import ScorecardRoutingPolicy
from apiforge.evals.evidence_coverage import calculate_evidence_coverage
from apiforge.governance.loop import check_loop
from apiforge.governance.recovery import decide_recovery
from apiforge.memory.store import persist_candidate, propose_memory, query_memory
from apiforge.runtime.scorecard_routing import assess_scorecard_routing
from apiforge.runtime.scorecard_shadow import evaluate_scorecard_shadow
from apiforge.trust.tools import authorize, load_tool_risk


def test_recovery_timeout_is_bounded() -> None:
    decision = decide_recovery("timeout", 99)
    assert decision.decision in {"escalate", "stop"}


def test_loop_detection_blocks_repeated_strategy() -> None:
    result = check_loop(["strategy:a", "strategy:a", "strategy:a"], max_repeats=2)
    assert result.blocked is True
    assert result.code == "AF-GOV-LOOP-DETECTED"


def test_tool_authorization_denial_is_explicit() -> None:
    profiles, permissions = load_tool_risk()
    result = authorize("critic", "memory_persist", profiles=profiles, permissions=permissions)
    assert result.decision == "deny"
    assert result.code == "AF-TOOL-DENIED"
    assert result.field and result.unlock


def test_memory_stale_is_ineligible_for_destructive_use(tmp_path) -> None:
    candidate = propose_memory(
        tmp_path,
        scope="task",
        origin="trusted_internal",
        payload={"fact": "stale"},
        proposed_by="lab",
        reason="fixture",
        created_at="2026-10-05T10:00:00Z",
        freshness="stale",
        trust_level="trusted",
        evidence_refs=("evidence:lab",),
    )
    assert persist_candidate(
        tmp_path,
        candidate,
        MemoryPolicy(policy_id="lab", minimum_trust="candidate"),
        now="2026-10-05T10:01:00Z",
    ).accepted
    result = query_memory(tmp_path, MemoryQuery(risk="destructive"))
    assert result.records == () and result.stale_count == 1


def test_memory_conflict_is_not_silent(tmp_path) -> None:
    for value in (300, 30):
        candidate = propose_memory(
            tmp_path,
            scope="task",
            origin="trusted_internal",
            payload={"timeout": value},
            proposed_by="lab",
            reason="fixture",
            created_at="2026-10-05T10:00:00Z",
            trust_level="trusted",
            evidence_refs=("evidence:lab",),
        )
        assert persist_candidate(
            tmp_path,
            candidate,
            MemoryPolicy(policy_id="lab", minimum_trust="candidate"),
            now="2026-10-05T10:01:00Z",
        ).accepted
    result = query_memory(tmp_path, MemoryQuery())
    assert result.status == "unresolved"
    assert result.conflicts


def test_context_missing_evidence_stays_partial() -> None:
    result = calculate_evidence_coverage(("contract", "policy"), ("contract",))
    assert result.state == "partial"
    assert result.missing == ("policy",)


def test_challenger_comparison_stays_shadow() -> None:
    assessment = assess_scorecard_routing(
        (
            CandidateAssessment(capability="champion", agent="a", eligible=True),
            CandidateAssessment(capability="challenger", agent="b", eligible=True),
        ),
        {
            "champion": AgentScorecard(
                agent="a",
                profile_id="a",
                evaluation_count=3,
                passed_count=3,
                quality_score=0.9,
                quality_promoted=True,
                freshness_state="fresh",
            )
        },
        ScorecardRoutingPolicy(challenger_slots=1),
    )
    result = evaluate_scorecard_shadow(
        assessment=assessment,
        baseline_policy_version="routing/v1",
        baseline_order=("challenger", "champion"),
        adaptive_order=("champion", "challenger"),
        baseline_selected="challenger",
        adaptive_selected="champion",
    )
    assert result.executed is False
    assert result.comparison == "reordered"
