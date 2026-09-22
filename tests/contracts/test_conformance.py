"""Golden round-trips and validator behavior for each canonical contract."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from apiforge.contracts.core import (
    ActionPlan,
    ArtifactRef,
    Decision,
    Verification,
)
from apiforge.contracts.graph import GraphEdge, GraphNode
from apiforge.contracts.stubs import (
    DataAccessIR,
    PerformanceRun,
    RuntimeMatrix,
    TelemetryEvent,
)
from apiforge.contracts.task import (
    AcceptanceRecord,
    CapabilityProof,
    OutcomeBrief,
    TaskHandoff,
    TaskPlan,
    TaskRevision,
    TaskSpec,
)
from apiforge.core.models import Fact, Finding, SourceRef
from apiforge.evidence.models import Receipt

SHA = "b" * 64


def _roundtrip(model: type, payload: dict) -> dict:
    obj = model.model_validate(payload)
    return obj.model_dump(mode="json")


def test_fact_backward_compatible_without_version() -> None:
    payload = {
        "fact_id": "f1",
        "kind": "code.route",
        "source": {"path": "a.py", "sha256": SHA},
    }
    fact = Fact.model_validate(payload)
    assert fact.version == 1


def test_finding_backward_compatible() -> None:
    payload = {
        "finding_id": "x",
        "rule_id": "AF-TEST-001",
        "status": "unresolved",
        "severity": "info",
        "title": "t",
    }
    assert Finding.model_validate(payload).version == 1


def test_receipt_keeps_schema_version() -> None:
    r = Receipt(case="c", policy_sha256=SHA, artifacts=())
    assert r.schema_version == "af-receipt/1"


def test_artifact_ref_roundtrip() -> None:
    out = _roundtrip(ArtifactRef, {"path": "a.json", "sha256": SHA, "kind": "report"})
    assert out["version"] == 1 and out["sha256"] == SHA


def test_decision_lifecycle() -> None:
    out = _roundtrip(
        Decision,
        {"id": "d1", "summary": "pick JSONL", "evidence": ["f1"]},
    )
    assert out["status"] == "proposed"


def test_action_plan_is_never_auto_applied() -> None:
    out = _roundtrip(
        ActionPlan,
        {
            "id": "p1",
            "steps": [{"verb": "build endpoint", "args": {"name": "x"}}],
            "risk": "sensitive",
        },
    )
    assert out["status"] == "proposed"
    assert out["risk"] == "sensitive"


def test_verification_unresolved_default() -> None:
    out = _roundtrip(Verification, {"id": "v1", "subject": "f1", "method": "hash"})
    assert out["result"] == "unresolved"


def test_taskspec_golden() -> None:
    out = _roundtrip(
        TaskSpec,
        {
            "id": "t1",
            "outcome": "add POST /orders",
            "writable_paths": ["app/routers/orders.py"],
            "budgets": {"max_calls": 5, "max_rounds": 1},
            "risk": "local_reversible",
            "strategy": "test-first",
            "acceptance_criteria": ["AF-CONTRACT-001 resolved"],
        },
    )
    assert out["state"] == "draft"
    assert out["budgets"]["max_calls"] == 5


def test_task_revision_seal_is_all_or_nothing() -> None:
    base = {"task_id": "t1", "revision": 1, "content_sha256": SHA}
    TaskRevision.model_validate(base)  # unsealed is fine
    with pytest.raises(ValidationError, match="seal requires"):
        TaskRevision.model_validate(base | {"sealed_by": "alice"})


def test_taskplan_steps_frozen() -> None:
    plan = TaskPlan.model_validate(
        {
            "task_id": "t1",
            "revision": 1,
            "recipe": "direct",
            "steps": [{"verb": "rules list"}],
        }
    )
    assert plan.steps[0]["verb"] == "rules list"


def test_handoff_records_parties() -> None:
    out = _roundtrip(
        TaskHandoff,
        {
            "task_id": "t1",
            "revision": 1,
            "from_agent": "api-contract-architect",
            "to_executor": "af-extractor",
            "context": ["facts.json"],
        },
    )
    assert out["to_executor"] == "af-extractor"


def test_acceptance_must_differ_from_executor() -> None:
    with pytest.raises(ValidationError, match="separate from the executor"):
        AcceptanceRecord.model_validate(
            {
                "task_id": "t1",
                "revision": 1,
                "verdict": "accepted",
                "accepted_by": "af-synthesizer",
                "executed_by": "af-synthesizer",
            }
        )
    ok = AcceptanceRecord.model_validate(
        {
            "task_id": "t1",
            "revision": 1,
            "verdict": "accepted",
            "accepted_by": "reviewer",
            "executed_by": "af-synthesizer",
        }
    )
    assert ok.verdict == "accepted"


def test_capability_proof() -> None:
    out = _roundtrip(
        CapabilityProof,
        {
            "capability": "spring route extraction",
            "proven_by": "tests/adapters/spring",
            "limitations": ["no SpEL evaluation"],
        },
    )
    assert out["capability"] == "spring route extraction"


def test_outcome_brief_done_refusals() -> None:
    # DONE with gaps is refused
    with pytest.raises(ValidationError, match="DONE refused"):
        OutcomeBrief.model_validate(
            {"status": "DONE", "outcome": "o", "proof": ["p"], "gaps": ["g"]}
        )
    # DONE without proof is refused
    with pytest.raises(ValidationError, match="proof"):
        OutcomeBrief.model_validate({"status": "DONE", "outcome": "o"})
    # DONE with pending human action is refused
    with pytest.raises(ValidationError, match="human_action"):
        OutcomeBrief.model_validate(
            {
                "status": "DONE",
                "outcome": "o",
                "proof": ["p"],
                "human_action": "deploy it",
            }
        )
    # clean DONE is accepted
    done = OutcomeBrief.model_validate({"status": "DONE", "outcome": "o", "proof": ["tests green"]})
    assert done.status.value == "DONE"
    # other statuses tolerate gaps
    blocked = OutcomeBrief.model_validate(
        {"status": "BLOCKED", "outcome": "o", "gaps": ["needs creds"]}
    )
    assert blocked.gaps == ("needs creds",)


def test_graph_vocabularies_are_closed() -> None:
    node = GraphNode.model_validate(
        {"id": "n1", "kind": "finding", "props": {"rule": "AF-SEC-101"}}
    )
    edge = GraphEdge.model_validate({"from_id": "n1", "to_id": "n2", "kind": "backed_by"})
    assert node.kind.value == "finding"
    assert edge.kind.value == "backed_by"
    with pytest.raises(ValidationError):
        GraphNode.model_validate({"id": "n", "kind": "not-a-kind"})
    with pytest.raises(ValidationError):
        GraphEdge.model_validate({"from_id": "a", "to_id": "b", "kind": "invented_edge"})


def test_stubs_carry_unresolved_surface() -> None:
    for model, extra in (
        (TelemetryEvent, {"name": "http.server.duration"}),
        (PerformanceRun, {"subject": "run-1"}),
        (DataAccessIR, {"database": "dynamodb"}),
        (RuntimeMatrix, {"subject": "spring-boot-3"}),
    ):
        out = _roundtrip(model, {"id": "s1", "unresolved": ["ttl"]} | extra)
        assert out["version"] == 1
        assert out["unresolved"] == ["ttl"]


def test_source_ref_and_shorthand_still_validate() -> None:
    ref = SourceRef(path="x.py", sha256=SHA, line=3)
    assert ref.extractor == "apiforge"
