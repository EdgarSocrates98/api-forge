import json
from pathlib import Path

from apiforge.contracts.agents import AgentRoutingCase
from apiforge.dispatch.agent_source import load_roster
from apiforge.dispatch.aliases import AliasTable
from apiforge.evals.agent_routing import compare, evaluate, run
from tests.dispatch.agent_support import write_agent

NONE = AliasTable(active=False, deprecated_in="", aliases={})


def _case(case_id: str, question: str, expected: str, family: str = "f") -> AgentRoutingCase:
    return AgentRoutingCase(
        id=case_id, question=question, expected=expected, family=family, source="test"
    )


def _roster(root: Path) -> None:
    write_agent(
        root,
        "api-adversarial-critic",
        description="Use when a high-risk plan must be refuted before approval. "
        "Not for closing debates (-> api-debate-referee).",
        tools=("debate packet",),
    )
    write_agent(
        root,
        "api-debate-referee",
        description="Use when a debate room needs quorum, dissent and a ruling. "
        "Not for attacking plans (-> api-adversarial-critic).",
        tools=("debate close",),
    )


def test_router_picks_distinct_protected_roles(tmp_path: Path) -> None:
    _roster(tmp_path)
    cases = (
        _case("A", "Refute this high-risk plan before approval", "api-adversarial-critic"),
        _case("B", "Close the debate room with quorum and a ruling", "api-debate-referee"),
    )
    report = evaluate(load_roster(tmp_path), cases, NONE)
    assert report.top1 == 1.0 and report.protected_misroutes == ()


def test_alias_mapping_scores_old_roster_against_new_labels(tmp_path: Path) -> None:
    write_agent(
        tmp_path,
        "api-grpc-parser-engineer",
        description="Use when a protobuf file must be parsed offline. Not for REST (-> other).",
    )
    table = AliasTable(
        active=False,
        deprecated_in="",
        aliases={"api-grpc-parser-engineer": "api-contract-architect"},
    )
    cases = (_case("A", "Parse this protobuf file offline", "api-contract-architect"),)
    report = evaluate(load_roster(tmp_path), cases, table)
    assert report.top1 == 1.0 and report.alias_mapping_applied


def test_misroute_of_protected_role_is_reported(tmp_path: Path) -> None:
    _roster(tmp_path)
    cases = (_case("A", "Close the debate room with quorum", "api-adversarial-critic"),)
    report = evaluate(load_roster(tmp_path), cases, NONE)
    assert report.protected_misroutes == ("A",)
    assert report.misses[0].predicted == "api-debate-referee"


def test_compare_gate() -> None:
    baseline = {"top1": 0.7, "top3": 0.9, "protected_misroutes": ["A", "B"]}
    assert compare({"top1": 0.8, "top3": 0.9, "protected_misroutes": []}, baseline)["ok"]
    worse = compare({"top1": 0.6, "top3": 0.95, "protected_misroutes": []}, baseline)
    assert not worse["ok"] and worse["checks"]["top1"] is False


def test_repository_corpus_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[2]
    first = run(root).model_dump(mode="json")
    second = run(root).model_dump(mode="json")
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["cases"] >= 60


def test_leakage_counts_copied_four_grams(tmp_path: Path) -> None:
    from apiforge.evals.agent_routing import leakage

    _roster(tmp_path)
    roster = load_roster(tmp_path)
    copied = _case("A", "a high-risk plan must be refuted now", "api-adversarial-critic")
    fresh = _case("B", "who settles the argument between reviewers", "api-debate-referee")
    assert leakage(roster, (copied, fresh)) == 0.5
