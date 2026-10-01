"""Graph call-site extraction, IR and sketch (AT-002..007)."""

from __future__ import annotations

from pathlib import Path

from apiforge.adapters.graph_.extract import blank_comments, extract_graph_access
from apiforge.adapters.graph_.ir import build_graph_access_ir
from apiforge.adapters.redis_.ir import build_data_access_ir
from apiforge.data_governance import assess_data_access, build_data_performance_profile
from apiforge.rules.fact_judge import judge_facts

GREMLIN_PY = "from gremlin_python.process.graph_traversal import __\n\n\ndef run(g):\n"


def _write(root: Path, name: str, body: str) -> Path:
    path = root / name
    path.write_text(body, encoding="utf-8")
    return path


def _rules(root: Path) -> list[str]:
    return sorted(f.rule_id for f in judge_facts(extract_graph_access(root).facts))


def test_multiline_python_chain_is_one_bounded_fact(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "q.py",
        GREMLIN_PY
        + "    return (\n        g.V()\n        .has_label('p')\n        .out('k')\n        .limit(5)\n    )\n",
    )
    facts = extract_graph_access(tmp_path).facts
    assert len(facts) == 1
    assert facts[0].measures["bounded"] is True
    assert facts[0].source.line == 6


def test_multiline_python_chain_unbounded_fires_once(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "q.py",
        GREMLIN_PY + "    return (g.V()\n        .has_label('p')\n        .out('k'))\n",
    )
    assert _rules(tmp_path) == ["AF-DATA-013"]


def test_repeat_without_stop_fires(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "q.py",
        GREMLIN_PY + "    return g.V().has_label('p').repeat(__.out('k')).limit(5)\n",
    )
    assert _rules(tmp_path) == ["AF-GDB-001"]


def test_java_neo4j_open_path(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "Q.java",
        "import org.neo4j.driver.Session;\nclass Q { Object r(Session session) {\n"
        '  return session.run("MATCH (a)-[*]->(b) RETURN b");\n} }\n',
    )
    fact = extract_graph_access(tmp_path).facts[0]
    assert fact.measures["vendor"] == "neo4j"
    assert fact.measures["language"] == "opencypher"
    assert "AF-GDB-004" in _rules(tmp_path)


def test_neptune_hint_switches_bolt_vendor(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "q.py",
        'from neo4j import GraphDatabase\nURI = "bolt://db.cluster.neptune.amazonaws.com:8182"\n\n'
        'def r(session):\n    return session.run("MATCH (n:P) RETURN n LIMIT 1")\n',
    )
    assert extract_graph_access(tmp_path).facts[0].measures["vendor"] == "neptune"
    assert extract_graph_access(tmp_path, "neo4j").facts == ()


def test_typescript_gremlin_and_heuristic_diagnostic(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "q.ts",
        "import gremlin from 'gremlin';\nexport const q = (g: any) => g.V().out().toList();\n",
    )
    inventory = extract_graph_access(tmp_path)
    assert [d.code for d in inventory.diagnostics] == ["AF-GDB-HEURISTIC"]
    assert {"AF-GDB-002", "AF-GDB-003", "AF-DATA-013"} == set(_rules(tmp_path))


def test_dynamic_query_is_unresolved_not_guessed(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "q.py",
        "from neo4j import GraphDatabase\n\ndef r(session, q):\n    return session.run(q)\n",
    )
    inventory = extract_graph_access(tmp_path)
    fact = inventory.facts[0]
    assert fact.measures["query_dynamic"] is True
    assert fact.measures["unbounded"] is False
    assert "AF-GDB-DYNAMIC-QUERY" in {d.code for d in inventory.diagnostics}
    assert _rules(tmp_path) == []


def test_comments_are_not_call_sites() -> None:
    text = 'a = "//x"; // g.V().out()\n/* g.V()\n.out() */ b'
    blanked = blank_comments(text)
    assert "g.V" not in blanked
    assert blanked.count("\n") == text.count("\n")
    assert '"//x"' in blanked


def test_ir_sketch_and_governance(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "q.py",
        "from neo4j import GraphDatabase\n\ndef r(session):\n"
        '    session.run("MATCH (a:Person)-[:KNOWS]->(b:Person) RETURN b LIMIT 5")\n'
        '    session.run("CREATE (n:Person {id: $id})", id=1)\n',
    )
    inventory = extract_graph_access(tmp_path)
    ir = build_graph_access_ir(inventory)
    assert ir.vendors == ("neo4j",)
    assert ("Person", "KNOWS", "Person") in ir.sketch.edges
    assert any(site.mutation for site in ir.call_sites)
    readiness = assess_data_access(
        build_data_access_ir(inventory, database="neo4j", provider="neo4j"),
        credential_configured=True,
    )
    assert "external-mutation-requires-approval" in readiness.blockers
    profile = build_data_performance_profile(inventory, database="neo4j")
    assert profile.latency_class == "graph"


def test_clean_tree_emits_nothing(tmp_path: Path) -> None:
    _write(tmp_path, "app.py", "import subprocess\nsubprocess.run(['ls'])\n")
    inventory = extract_graph_access(tmp_path)
    assert inventory.facts == () and inventory.diagnostics == ()
