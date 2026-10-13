"""Pure Gremlin/openCypher/SPARQL analyzers — declared shape only, no execution."""

from __future__ import annotations

import pytest

from apiforge.adapters.graph_ import cypher, gremlin, sparql


@pytest.mark.parametrize(
    ("text", "risks", "bounded"),
    [
        ("g.V().repeat(out('knows')).emit()", {"repeat-without-stop", "unfiltered-start"}, False),
        ("g.V().hasLabel('p').repeat(out('k')).times(3).limit(5)", set(), True),
        ("g.V().hasLabel('p').both()", {"fanout-without-edge-label"}, False),
        ("g.V().valueMap()", {"unfiltered-start"}, False),
        ("g.V().limit(1)", set(), True),
        ("g.V(id).out('a').next()", set(), True),
        ('g.V().HasLabel("p").Out("k").Limit(3)', set(), True),
        ("g.V().has_label('p').in_()", {"fanout-without-edge-label"}, False),
        ("g.V().hasLabel('p').repeat(__.out('k')).until(has('name', 'x'))", set(), False),
    ],
)
def test_gremlin_shapes(text: str, risks: set[str], bounded: bool) -> None:
    result = gremlin.analyze(text)
    assert set(result["shape_risks"]) == risks
    assert result["bounded"] is bounded


def test_gremlin_labels_and_mutation() -> None:
    result = gremlin.analyze("g.V().has('person','name','x').out('knows').addE('likes')")
    assert result["labels_used"] == ("person",)
    assert result["edge_labels_used"] == ("knows", "likes")
    assert result["mutation"] is True
    assert gremlin.analyze("g.V().properties('x').limit(1)")["mutation"] is False


@pytest.mark.parametrize(
    ("text", "risks", "bounded", "mutation"),
    [
        ("MATCH (a:P)-[:K*]->(b) RETURN b LIMIT 1", {"open-variable-length-path"}, True, False),
        ("MATCH (a:P)-[:K*2..]->(b) RETURN b", {"open-variable-length-path"}, False, False),
        ("MATCH (a:P)-[:K*1..3]->(b:P) RETURN b LIMIT 1", set(), True, False),
        ("MATCH (a:P)-[:K*3]->(b:P) RETURN b LIMIT 1", set(), True, False),
        ("MATCH (n) RETURN n LIMIT 5", {"unlabeled-node-pattern"}, True, False),
        ("MATCH (n {code: 'ATL'}) RETURN n LIMIT 1", set(), True, False),
        ("MATCH (a:P) WITH a MATCH (a)-[:K]->(b) RETURN b LIMIT 1", set(), True, False),
        ("MATCH (a:P), (b:Q) RETURN a, b LIMIT 5", {"cartesian-pattern"}, True, False),
        ("MATCH (a:P)-[:K]->(b), (b)-[:L]->(c:Q) RETURN c LIMIT 5", set(), True, False),
        ("MATCH (a:P {id: $id})-[:K]->(b:P) RETURN count(b)", set(), True, False),
        ("CREATE (n:X {name: 'MATCH (m) RETURN m'})", set(), False, True),
        ("MERGE (n:X {id: $id}) ON CREATE SET n.c = 1", set(), False, True),
        ("MATCH (n:P) WHERE n.name = 'LIMIT 5' RETURN n", set(), False, False),
    ],
)
def test_cypher_shapes(text: str, risks: set[str], bounded: bool, mutation: bool) -> None:
    result = cypher.analyze(text)
    assert set(result["shape_risks"]) == risks
    assert result["bounded"] is bounded
    assert result["mutation"] is mutation


def test_cypher_analytics_and_vectors() -> None:
    assert cypher.analyze("CALL neptune.algo.pageRank.mutate({writeProperty: 'r'})")[
        "shape_risks"
    ] == ("analytics-unscoped-algorithm",)
    scoped = "MATCH (n:airport) CALL neptune.algo.pageRank(n) YIELD rank RETURN n, rank LIMIT 1"
    assert cypher.analyze(scoped)["shape_risks"] == ()
    assert cypher.analyze("CALL neptune.algo.vectors.topKByNode('n1') YIELD node RETURN node")[
        "shape_risks"
    ] == ("vector-search-without-topk",)
    assert (
        cypher.analyze("CALL neptune.algo.vectors.topK.byEmbedding([0.1], {topK: 5})")[
            "shape_risks"
        ]
        == ()
    )
    assert cypher.analyze("CALL neptune.algo.vectors.upsert('n1', [0.1])")["shape_risks"] == ()


def test_cypher_triples_and_labels() -> None:
    result = cypher.analyze("MATCH (a:Person)-[:KNOWS]->(b:Person) RETURN b LIMIT 1")
    assert result["labels_used"] == ("Person",)
    assert result["edge_labels_used"] == ("KNOWS",)


@pytest.mark.parametrize(
    ("text", "risks", "bounded", "mutation"),
    [
        ("SELECT * WHERE { ?s :knows+ ?o }", {"unbounded-property-path"}, False, False),
        (
            "SELECT ?x WHERE { ?x <http://x/p>* ?y } LIMIT 5",
            {"unbounded-property-path"},
            True,
            False,
        ),
        ("SELECT * WHERE { ?s ?p ?o } LIMIT 5", set(), True, False),
        ("SELECT (COUNT(*) AS ?c) WHERE { ?s ?p ?o }", set(), True, False),
        ("ASK { ?s a :Person }", set(), True, False),
        ("SELECT ?x WHERE { ?x :v ?v . FILTER(?v * 2 > 1) }", set(), False, False),
        ("INSERT DATA { :a :b :c }", set(), False, True),
        ("DELETE WHERE { ?s ?p ?o }", set(), False, True),
    ],
)
def test_sparql_shapes(text: str, risks: set[str], bounded: bool, mutation: bool) -> None:
    result = sparql.analyze(text)
    assert set(result["shape_risks"]) == risks
    assert result["bounded"] is bounded
    assert result["mutation"] is mutation
