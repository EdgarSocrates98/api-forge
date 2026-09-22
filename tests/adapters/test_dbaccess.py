"""MongoDB/DynamoDB/Neptune data-access extraction — facts + IR + rules."""

from __future__ import annotations

from pathlib import Path

from apiforge.adapters.dbaccess import (
    extract_dynamo_access,
    extract_mongo,
    extract_neptune_access,
)
from apiforge.adapters.redis_.ir import build_data_access_ir
from apiforge.rules.fact_judge import judge_facts

FIXTURE = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "dbaccess_app"


def _findings(inv, rule_id: str):
    return [f for f in judge_facts(inv.facts) if f.rule_id == rule_id]


def test_mongo_facts_and_rules() -> None:
    inv = extract_mongo(FIXTURE)
    ops = [
        f
        for f in inv.facts
        if f.kind == "data.mongo.operation"
        and f.source.path == "mongo_repo.py"
    ]
    assert ops
    by_op = {}
    for f in ops:
        by_op.setdefault(f.measures["operation"], []).append(f.measures)
    # find: .limit(50) chain and limit= kwarg are bounded; bare find({}) is not
    finds = by_op["find"]
    unbounded = [f for f in finds if f["unbounded_find"]]
    bounded = [f for f in finds if not f["unbounded_find"]]
    assert len(unbounded) == 1 and len(bounded) == 2
    # delete_many({}) -> unfiltered; update_many with literal -> filtered
    assert by_op["delete_many"][0]["unfiltered_write"] is True
    assert by_op["update_many"][0]["unfiltered_write"] is False
    assert _findings(inv, "AF-DATA-011")
    assert _findings(inv, "AF-DATA-012")
    # entity literals collected (collection names, not values)
    entities = {f.measures.get("entity") for f in ops}
    assert "orders" in entities and "sessions" in entities
    assert any(d.code == "AF-MONGO-HEURISTIC-BINDING" for d in inv.diagnostics)


def test_dynamo_facts_and_rules() -> None:
    inv = extract_dynamo_access(FIXTURE)
    ops = [
        f
        for f in inv.facts
        if f.kind == "data.dynamo.operation"
        and f.source.path == "dynamo_repo.py"
    ]
    scans = [f for f in ops if f.measures["operation"] == "scan"]
    assert len(scans) == 2
    full = [f for f in scans if f.measures["full_scan"]]
    assert len(full) == 1
    queries = [f for f in ops if f.measures["operation"] == "query"]
    assert [q.measures["query_without_key_condition"] for q in queries].count(
        True
    ) == 1
    assert _findings(inv, "AF-DATA-009")
    assert _findings(inv, "AF-DATA-010")
    tables = {
        f.measures["entity"]
        for f in inv.facts
        if f.kind == "data.dynamo.table_ref"
    }
    assert tables == {"orders"}


def test_neptune_facts_and_rules() -> None:
    inv = extract_neptune_access(FIXTURE)
    queries = [f for f in inv.facts if f.kind == "data.neptune.query"]
    gremlin = [f for f in queries if f.measures["language"] == "gremlin"]
    cypher = [f for f in queries if f.measures["language"] == "opencypher"]
    assert len(gremlin) == 2 and len(cypher) == 2
    # bounded gremlin traversal on the same line
    assert sum(1 for f in gremlin if f.measures["unbounded"]) == 1
    # cypher with LIMIT is bounded; without is not
    assert sum(1 for f in cypher if f.measures["unbounded"]) == 1
    assert len(_findings(inv, "AF-DATA-013")) == 2


def test_java_pattern_facts() -> None:
    inv = extract_mongo(FIXTURE)
    java = [
        f for f in inv.facts if f.source.path.endswith("Store.java")
    ]
    assert java
    assert any(
        f.measures["operation"] == "deletemany"
        and f.measures.get("unfiltered_write") is True
        for f in java
    )
    dinv = extract_dynamo_access(FIXTURE)
    java_d = [
        f for f in dinv.facts if f.source.path.endswith("Store.java")
    ]
    scans = [f for f in java_d if f.measures["operation"] == "scan"]
    assert len(scans) == 2
    assert sum(1 for f in scans if f.measures.get("full_scan")) == 1


def test_ir_aggregates_all_databases() -> None:
    for extract, database in (
        (extract_mongo, "mongodb"),
        (extract_dynamo_access, "dynamodb"),
        (extract_neptune_access, "neptune"),
    ):
        inv = extract(FIXTURE)
        ir = build_data_access_ir(
            inv, database=database, provider=database
        )
        assert ir.database == database
        assert ir.access_patterns
        assert ir.unresolved  # heuristic binding is named


def test_clean_project_emits_nothing(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    for extract in (extract_mongo, extract_dynamo_access, extract_neptune_access):
        inv = extract(tmp_path)
        assert inv.facts == ()
        assert inv.diagnostics == ()
