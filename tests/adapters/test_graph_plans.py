"""Plan dumps -> GraphPlanIR + data.graph.plan facts (AT-008/009, AF-GDB-020..025)."""

from __future__ import annotations

from pathlib import Path

import pytest

from apiforge.adapters.graph_.plans import PlanError, detect_format, extract_graph_plan, parse_plan
from apiforge.rules.fact_judge import judge_facts

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "graph_explain"

CASES = {
    "gremlin-explain.txt": ("neptune-gremlin-explain", False, {"AF-GDB-020", "AF-GDB-021"}),
    "gremlin-profile.txt": ("neptune-gremlin-profile", True, set()),
    "cypher-static.txt": ("neptune-opencypher-static", False, {"AF-GDB-023"}),
    "cypher-dynamic.txt": ("neptune-opencypher-dynamic", True, {"AF-GDB-023", "AF-GDB-025"}),
    "sparql-explain.txt": ("neptune-sparql-explain", False, set()),
    "neo4j-explain.txt": ("neo4j-explain", False, {"AF-GDB-024"}),
    "neo4j-profile.txt": ("neo4j-profile", True, {"AF-GDB-025"}),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_every_fixture_parses_and_judges(name: str) -> None:
    fmt, executed, rules = CASES[name]
    inventory, plan = extract_graph_plan(FIXTURES / name, synthetic=True)
    assert plan.format == fmt
    assert plan.executed is executed
    assert plan.synthetic is True
    assert plan.operators
    assert {f.rule_id for f in judge_facts(inventory.facts)} == rules


def test_executed_ratio_only_for_executed_plans() -> None:
    inventory, _ = extract_graph_plan(FIXTURES / "cypher-static.txt")
    assert "max_fanout_ratio" not in inventory.facts[0].measures


def test_non_native_steps_are_split_at_top_level() -> None:
    _, plan = extract_graph_plan(FIXTURES / "gremlin-explain.txt")
    names = [op.name for op in plan.operators if not op.native]
    assert names == ["FoldStep", "UnfoldStep", "VertexStep"]
    assert plan.predicate_count == 18


def test_unknown_dump_refuses_with_unlock() -> None:
    with pytest.raises(PlanError) as caught:
        detect_format("hello")
    assert caught.value.code == "AF-GDB-PLAN-FORMAT"
    assert caught.value.field == "path" and "--format" in caught.value.unlock


def test_empty_plan_refuses() -> None:
    with pytest.raises(PlanError, match="AF-GDB-PLAN-PARSE"):
        parse_plan("Neptune Gremlin Explain\n", "neptune-gremlin-explain")


def test_missing_file_refuses(tmp_path: Path) -> None:
    with pytest.raises(PlanError, match="AF-GDB-PLAN-PARSE"):
        extract_graph_plan(tmp_path / "absent.txt")


def test_collector_json_payload_is_read(tmp_path: Path) -> None:
    import json

    dump = tmp_path / "plan.json"
    text = (FIXTURES / "gremlin-explain.txt").read_text(encoding="utf-8")
    dump.write_text(json.dumps({"output": text}), encoding="utf-8")
    _, plan = extract_graph_plan(dump)
    assert plan.format == "neptune-gremlin-explain"
