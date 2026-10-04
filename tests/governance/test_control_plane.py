"""§28-§32 Decision Control Plane lifecycle tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.contracts.agentic import ApprovalGate
from apiforge.contracts.agentic_governance import PromotionEvidence, ShadowRecord
from apiforge.economy.run_ledger import EconomyError
from apiforge.governance.control_plane import (
    demote,
    detect_triggers,
    diff_decisions,
    evaluate_route,
    promote,
    route_status,
    select_fallback,
    shadow_records,
)


def _routes_file(tmp_path: Path, routes: list[dict[str, object]]) -> Path:
    path = tmp_path / "routes.yaml"
    path.write_text(
        "version: 1\nroutes:\n"
        + "".join(
            f"  - route: {r['route']}\n"
            f"    mode: {r['mode']}\n"
            f"    candidate: {r['candidate']}\n"
            f"    legacy: {r['legacy']}\n"
            f"    fallback_route: {r.get('fallback_route') or 'null'}\n"
            for r in routes
        ),
        encoding="utf-8",
    )
    return path


def _declared(tmp_path: Path) -> dict[str, object]:
    from apiforge.governance.control_plane import load_routes

    routes = [
        {
            "route": "model_routing",
            "mode": "shadow",
            "candidate": "model-router-v1",
            "legacy": "provider-tier-descriptor",
            "fallback_route": "provider_descriptor",
        },
        {
            "route": "terminal",
            "mode": "active",
            "candidate": "leaf",
            "legacy": "leaf",
            "fallback_route": None,
        },
    ]
    return load_routes(_routes_file(tmp_path, routes))


def test_route_status_defaults_to_declared_mode(tmp_path: Path) -> None:
    routes = _declared(tmp_path)
    status = route_status(tmp_path, "model_routing", routes=routes)
    assert status.mode == "shadow"
    assert status.fallback_route == "provider_descriptor"


def test_unknown_route_refuses(tmp_path: Path) -> None:
    with pytest.raises(EconomyError) as err:
        route_status(tmp_path, "nope", routes=_declared(tmp_path))
    assert "AF-GOV-ROUTE-UNKNOWN" in str(err.value)


def test_diff_decisions_sorted_and_complete() -> None:
    assert diff_decisions({"a": 1, "b": 2}, {"a": 1, "b": 3, "c": 0}) == ("b", "c")


def test_shadow_eval_records_and_legacy_governs(tmp_path: Path) -> None:
    routes = _declared(tmp_path)
    decision = evaluate_route(
        tmp_path,
        "model_routing",
        candidate_decision={"model": "new"},
        legacy_decision={"model": "old"},
        confidence=0.8,
        evidence_refs=("fact:1",),
        routes=routes,
    )
    assert decision.governing == "legacy"
    assert decision.shadow is True
    records = shadow_records(tmp_path, "model_routing")
    assert len(records) == 1
    assert records[0].difference == ("model",)
    assert records[0].confidence == 0.8


def test_assisted_recommends_but_legacy_governs(tmp_path: Path) -> None:
    routes = _declared(tmp_path)
    demote(tmp_path, "terminal", routes=routes)  # active -> assisted
    decision = evaluate_route(
        tmp_path,
        "terminal",
        candidate_decision={"model": "new"},
        legacy_decision={"model": "old"},
        routes=routes,
    )
    assert decision.mode == "assisted"
    assert decision.governing == "legacy"
    assert decision.recommendation == {"model": "new"}


def test_active_candidate_governs_without_trigger(tmp_path: Path) -> None:
    routes = _declared(tmp_path)
    decision = evaluate_route(tmp_path, "terminal", routes=routes)
    assert decision.mode == "active"
    assert decision.governing == "candidate"
    assert decision.fallback is not None and decision.fallback.action == "continue_active"


def test_active_trigger_uses_declared_fallback(tmp_path: Path) -> None:
    routes = _declared(tmp_path)
    # promote model_routing shadow -> assisted -> active via overlay rows
    (tmp_path / ".apiforge" / "control-plane").mkdir(parents=True)
    modes = tmp_path / ".apiforge" / "control-plane" / "modes.jsonl"
    modes.write_text(
        json.dumps(
            {
                "route": "model_routing",
                "mode": "active",
                "candidate": "model-router-v1",
                "legacy": "provider-tier-descriptor",
                "fallback_route": "provider_descriptor",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    decision = evaluate_route(
        tmp_path, "model_routing", triggers=("provider_issue",), routes=routes
    )
    assert decision.governing == "none"
    assert decision.fallback is not None
    assert decision.fallback.action == "use_fallback"
    assert decision.fallback.fallback_route == "provider_descriptor"


def test_terminal_route_degrades_to_refuse(tmp_path: Path) -> None:
    routes = _declared(tmp_path)
    fallback = select_fallback(route_status(tmp_path, "terminal", routes=routes), "security_issue")
    assert fallback.action == "refuse"
    assert fallback.code == "AF-GOV-FALLBACK-MISSING"


def test_detect_triggers_closed_vocabulary() -> None:
    found = detect_triggers(
        confidence=0.2,
        evidence_complete=False,
        security_issue=True,
        provider_issue=False,
        budget_issue=True,
    )
    assert found == ("low_confidence", "missing_evidence", "security_issue", "budget_issue")
    quiet = detect_triggers(
        confidence=None,
        evidence_complete=True,
        security_issue=False,
        provider_issue=False,
        budget_issue=False,
    )
    assert quiet == ()


def _evidence(route: str, **over: object) -> PromotionEvidence:
    base: dict[str, object] = {
        "route": route,
        "eval_thresholds_passed": True,
        "security_gates_passed": True,
        "evidence_complete": True,
        "rollback_exists": True,
        "approval_id": "gate-1",
    }
    base.update(over)
    return PromotionEvidence.model_validate(base)


def test_promote_shadow_to_assisted_needs_evidence(tmp_path: Path) -> None:
    routes = _declared(tmp_path)
    denied = promote(
        tmp_path,
        "model_routing",
        _evidence("model_routing", evidence_complete=False),
        routes=routes,
    )
    assert denied.allowed is False
    assert denied.code == "AF-GOV-PROMOTION-INCOMPLETE"
    assert "evidence_complete" in denied.missing

    allowed = promote(tmp_path, "model_routing", _evidence("model_routing"), routes=routes)
    assert allowed.allowed is True
    assert allowed.to_mode == "assisted"
    assert route_status(tmp_path, "model_routing", routes=routes).mode == "assisted"


def test_promote_active_needs_all_five_and_approval(tmp_path: Path) -> None:
    routes = _declared(tmp_path)
    promote(tmp_path, "model_routing", _evidence("model_routing"), routes=routes)

    missing = promote(
        tmp_path,
        "model_routing",
        _evidence("model_routing", rollback_exists=False, approval_id=None),
        routes=routes,
    )
    assert missing.allowed is False
    assert "rollback_exists" in missing.missing
    assert "approval_id" in missing.missing

    no_gate = promote(tmp_path, "model_routing", _evidence("model_routing"), routes=routes)
    assert no_gate.code == "AF-GOV-PROMOTION-NOT-APPROVED"

    gate = ApprovalGate(
        gate_id="gate-1",
        run_id="run-1",
        reason="promote model_routing to active",
        requested_action="control_promote",
        status="approved",
        requested_by="operator",
        decided_by="human",
    )
    promoted = promote(
        tmp_path, "model_routing", _evidence("model_routing"), approval=gate, routes=routes
    )
    assert promoted.allowed is True
    assert promoted.to_mode == "active"
    status = route_status(tmp_path, "model_routing", routes=routes)
    assert status.mode == "active"
    assert status.promotion_approval_id == "gate-1"


def test_promote_active_refuses_second_step(tmp_path: Path) -> None:
    routes = _declared(tmp_path)
    refused = promote(tmp_path, "terminal", _evidence("terminal"), routes=routes)
    assert refused.allowed is False
    assert refused.code == "AF-GOV-MODE-TRANSITION-INVALID"


def test_demote_always_allowed(tmp_path: Path) -> None:
    routes = _declared(tmp_path)
    demoted = demote(tmp_path, "terminal", routes=routes)
    assert demoted.mode == "assisted"
    again = demote(tmp_path, "terminal", routes=routes)
    assert again.mode == "shadow"
    floor = demote(tmp_path, "terminal", routes=routes)
    assert floor.mode == "shadow"


def test_shadow_record_roundtrip(tmp_path: Path) -> None:
    record = ShadowRecord(
        route="model_routing",
        candidate_decision={"x": 1},
        legacy_decision={"x": 2},
        difference=("x",),
        confidence=0.9,
        evidence_refs=("fact:1",),
        recorded_at="2026-10-06T00:00:00Z",
    )
    assert record.model_dump(mode="json")["schema"] == "apiforge/shadow-record/v1"
