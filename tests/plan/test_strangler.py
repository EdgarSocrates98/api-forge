"""strangler_plan: baseline vs candidate code.route facts -> cut plan."""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.adapters.fastapi.extractor import extract_fastapi
from apiforge.adapters.spring.extractor import extract_spring
from apiforge.core.models import Fact, SourceRef
from apiforge.plan.strangler import strangler_plan

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
LABS = Path(__file__).resolve().parents[1] / "labs"


def _routes(inv) -> list[Fact]:
    return [f for f in inv.facts if f.kind == "code.route"]


def test_missing_routes_block_the_cut() -> None:
    base = _routes(extract_fastapi(FIXTURES / "fastapi_orders"))
    cand = _routes(extract_spring(LABS / "orders-spring"))
    plan = strangler_plan(base, cand)
    # both labs serve /v1/orders surfaces; check statuses are all named
    assert {i["status"] for i in plan["items"]} <= {
        "migrated",
        "missing",
        "stale",
        "added",
    }
    assert plan["cut_ready"] == (plan["counts"]["missing"] == 0)
    migrated = [i for i in plan["items"] if i["status"] == "migrated"]
    for item in migrated:
        assert item["cut_requires"]  # parity evidence named, never claimed
        assert item["evidence_fact"].startswith("fact:")


def test_identical_surfaces_are_cut_ready() -> None:
    base = _routes(extract_fastapi(FIXTURES / "fastapi_orders"))
    plan = strangler_plan(base, base)
    assert plan["cut_ready"] is True
    assert plan["counts"]["missing"] == 0
    assert plan["counts"]["added"] == 0


def test_candidate_only_routes_are_added_not_blockers(tmp_path: Path) -> None:
    base = _routes(extract_fastapi(FIXTURES / "fastapi_orders"))
    extra = Fact(
        fact_id="fact:extra",
        kind="code.route",
        source=SourceRef(path="app.py", sha256="0" * 64, extractor="test"),
        measures={"method": "GET", "path": "/health"},
        attrs={"reachable": True},
    )
    plan = strangler_plan(base, [*base, extra])
    added = [i for i in plan["items"] if i["status"] == "added"]
    assert len(added) == 1
    assert added[0]["path"] == "/health"
    assert added[0]["cut_requires"] == []


def test_facts_round_trip_via_cli_shape(tmp_path: Path) -> None:
    """strangler consumes the same facts.json payload judge --facts reads."""
    inv = extract_fastapi(FIXTURES / "fastapi_orders")
    payload = {"facts": [f.model_dump(mode="json") for f in inv.facts]}
    f = tmp_path / "facts.json"
    f.write_text(json.dumps(payload), encoding="utf-8")
    doc = json.loads(f.read_text())
    facts = [Fact.model_validate(x) for x in doc["facts"]]
    plan = strangler_plan(facts, facts)
    assert plan["baseline_routes"] > 0
