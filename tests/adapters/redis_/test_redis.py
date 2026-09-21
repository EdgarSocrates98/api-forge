"""Redis/Valkey extractor — facts, DataAccessIR, and AF-DATA-* rule coverage."""

from __future__ import annotations

from pathlib import Path

import pytest

from apiforge.adapters.redis_.extract import extract_redis
from apiforge.adapters.redis_.ir import build_data_access_ir
from apiforge.rules.fact_judge import judge_facts

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "redis_app"


def _facts() -> tuple:
    return extract_redis(FIXTURE).facts


def test_extracts_commands_across_languages() -> None:
    facts = _facts()
    commands = {
        f.measures["command"]
        for f in facts
        if f.kind == "data.redis.command"
    }
    assert {"get", "set", "setex", "keys", "flushall", "flushdb",
            "config", "debug", "monitor", "save"} <= commands
    langs = {f.source.path.rsplit(".", 1)[-1] for f in facts}
    assert {"py", "go", "java"} <= langs


def test_python_constructor_binding_proven() -> None:
    facts = _facts()
    py = [f for f in facts if f.source.path.endswith(".py")]
    assert py
    assert all(f.measures.get("binding") == "constructor" for f in py)


def test_java_go_bindings_are_name_heuristics() -> None:
    facts = _facts()
    non_py = [f for f in facts if not f.source.path.endswith(".py")]
    assert non_py
    assert all(f.measures.get("binding") == "name" for f in non_py)
    diags = extract_redis(FIXTURE).diagnostics
    assert any(d.code == "AF-REDIS-HEURISTIC-BINDING" for d in diags)


def test_ttl_visible_on_setex_absent_on_set() -> None:
    writes = {
        (f.source.path, f.measures["command"]): f
        for f in _facts()
        if f.kind == "data.redis.write"
    }
    setex = [f for (p, c), f in writes.items() if c == "setex"]
    plain = [f for (p, c), f in writes.items() if c == "set"]
    assert setex and all("ttl_seconds" in f.measures for f in setex)
    assert plain and all("ttl_seconds" not in f.measures for f in plain)


def test_dangerous_commands_fire_rules() -> None:
    fired = {f.rule_id for f in judge_facts(_facts())}
    assert "AF-DATA-001" in fired  # keys
    assert "AF-DATA-003" in fired  # flushall
    assert "AF-DATA-004" in fired  # flushdb
    assert "AF-DATA-005" in fired  # config_set -> "config" family? see note
    assert "AF-DATA-006" in fired  # debug
    assert "AF-DATA-007" in fired  # monitor
    assert "AF-DATA-008" in fired  # save


def test_write_without_ttl_fires() -> None:
    fired = [f for f in judge_facts(_facts()) if f.rule_id == "AF-DATA-002"]
    assert fired  # set() calls without ttl in py/go/java
    setex_facts = [
        f for f in _facts()
        if f.kind == "data.redis.write" and f.measures["command"] == "setex"
    ]
    setex_ids = {f.fact_id for f in setex_facts}
    for finding in fired:
        assert not set(finding.evidence) & setex_ids


def test_clean_code_stays_quiet(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text(
        "import redis\nr = redis.Redis()\nr.setex('k', 60, 'v')\nr.get('k')\n",
        encoding="utf-8",
    )
    findings = judge_facts(extract_redis(tmp_path).facts)
    assert findings == ()


def test_no_redis_import_no_facts(tmp_path: Path) -> None:
    (tmp_path / "plain.py").write_text("x = 1\n", encoding="utf-8")
    inventory = extract_redis(tmp_path)
    assert inventory.facts == ()
    assert inventory.diagnostics == ()


def test_syntax_error_is_diagnostic_not_crash(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text("def broken(:\n", encoding="utf-8")
    inventory = extract_redis(tmp_path)
    assert any(d.code == "AF-REDIS-PARSE" for d in inventory.diagnostics)


def test_data_access_ir_populated() -> None:
    inventory = extract_redis(FIXTURE)
    ir = build_data_access_ir(inventory)
    assert ir.database == "redis"
    assert ir.provider == "redis|valkey"
    assert ir.entities  # literal keys collected
    assert ir.access_patterns  # distinct commands
    assert ir.unresolved  # heuristic binding named


def test_extraction_is_deterministic() -> None:
    a = extract_redis(FIXTURE)
    b = extract_redis(FIXTURE)
    assert [f.fact_id for f in a.facts] == [f.fact_id for f in b.facts]
    assert [d.code for d in a.diagnostics] == [d.code for d in b.diagnostics]


def test_rule_evidence_cites_fact_ids() -> None:
    for finding in judge_facts(_facts()):
        assert finding.evidence, finding.rule_id
        for ev in finding.evidence:
            assert ev.startswith("fact:"), ev


@pytest.mark.parametrize("rule_id", [
    "AF-DATA-001", "AF-DATA-002", "AF-DATA-003", "AF-DATA-004",
    "AF-DATA-005", "AF-DATA-006", "AF-DATA-007", "AF-DATA-008",
])
def test_every_data_rule_fires_on_lab(rule_id: str) -> None:
    fired = {f.rule_id for f in judge_facts(_facts())}
    assert rule_id in fired
