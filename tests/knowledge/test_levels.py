"""§36-§39 adaptive retrieval, semantic adapter and query rewrite tests."""

from __future__ import annotations

import pytest

from apiforge.contracts.graph import GraphEdge, GraphNode
from apiforge.graph.store import write_graph
from apiforge.knowledge.levels import adaptive_retrieve, load_level_policy
from apiforge.knowledge.rewrite import rewrite_query
from apiforge.knowledge.semantic import HashEmbeddingAdapter


def test_policy_loads() -> None:
    rules = load_level_policy()
    assert rules["levels"]["L1"]["min_hits"] == 3
    assert rules["hybrid"]["lexical"] == pytest.approx(0.6)


def test_exact_lookup_stops_at_l0() -> None:
    result = adaptive_retrieve("openapi", max_level="L4")
    levels = [step.level for step in result.steps]
    assert levels[0] == "L0"
    if result.level_used == "L0":
        assert len(levels) == 1


def test_escalation_stops_when_sufficient() -> None:
    result = adaptive_retrieve("openapi", max_level="L4")
    used = [step.level for step in result.steps]
    assert result.level_used == used[-1]
    assert not result.steps[-1].escalated
    # never escalates past what is needed
    assert len(used) <= 4


def test_semantic_undeclared_marks_unresolved() -> None:
    result = adaptive_retrieve("zz-no-match-term-qq", semantic=None, max_level="L4")
    assert "semantic" in result.unresolved
    l3 = next(step for step in result.steps if step.level == "L3")
    assert l3.reason == "adapter undeclared"
    assert result.semantic_available is False


def test_hash_adapter_deterministic_and_bounded() -> None:
    adapter = HashEmbeddingAdapter()
    score_a = adapter.score(("oauth", "token"), "OAuth token refresh flow")
    score_b = adapter.score(("oauth", "token"), "OAuth token refresh flow")
    assert score_a == score_b
    assert 0.0 <= score_a <= 1.0
    assert adapter.score(("unrelated",), "completely different text") >= 0.0
    assert adapter.score((), "text") == 0.0


def test_semantic_level_can_add_a_non_lexical_candidate() -> None:
    class CandidateAdapter:
        def score(self, query_terms: tuple[str, ...], text: str) -> float:
            return 1.0

        def candidates(
            self, query_terms: tuple[str, ...], documents: tuple[tuple[str, str], ...]
        ) -> tuple[tuple[str, float], ...]:
            return ((documents[0][0], 1.0),) if documents else ()

    result = adaptive_retrieve("zz-no-lexical-hit-qq", semantic=CandidateAdapter(), max_level="L3")
    assert result.semantic_available is True
    assert result.hits
    assert all(
        any("semantic-candidate" in ref for ref in refs) for refs in result.provenance.values()
    )


def test_graph_level_traverses_declared_graph(tmp_path) -> None:
    graph_dir = tmp_path / "graph"
    write_graph(
        graph_dir,
        [
            GraphNode(id="service:orders", kind="service"),
            GraphNode(id="handler:orders", kind="handler"),
            GraphNode(id="test:orders", kind="test"),
        ],
        [
            GraphEdge(from_id="service:orders", to_id="handler:orders", kind="implemented_by"),
            GraphEdge(from_id="handler:orders", to_id="test:orders", kind="verified_by"),
        ],
    )
    result = adaptive_retrieve("service orders", max_level="L2", graph_dir=graph_dir)
    assert result.level_used == "L2"
    assert len(result.hits) >= 3
    assert sum(
        any("knowledge:graph" in ref for ref in refs) for refs in result.provenance.values()
    ) >= 3


def test_rewrite_gates() -> None:
    ok = rewrite_query("mystery", deterministic_hits=0, profile="balanced")
    assert ok.gate == "allowed"
    assert ok.rewritten is not None
    assert ok.original == "mystery"

    done = rewrite_query("found", deterministic_hits=3)
    assert done.gate == "deterministic_succeeded"
    assert done.rewritten is None

    broke = rewrite_query("x", deterministic_hits=0, budget_remaining={"rewrites": 0})
    assert broke.gate == "budget_blocked"

    eco = rewrite_query("x", deterministic_hits=0, profile="economy")
    assert eco.gate == "profile_blocked"


def test_rewrite_uses_declared_expansion() -> None:
    result = rewrite_query("auth", deterministic_hits=0, profile="deep")
    assert result.gate == "allowed"
    assert result.rewritten is not None
    assert result.original in result.rewritten
