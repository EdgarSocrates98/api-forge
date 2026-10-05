"""Trust Plane contract invariants: DATA IS NOT INSTRUCTION."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from apiforge.contracts.trust import (
    AgentPermissionSet,
    MemoryGateResult,
    MemoryQuarantine,
    ToolAuthorization,
    ToolRiskProfile,
    TrustPropagation,
    TrustUnit,
)


def test_data_origins_never_carry_instruction_authority() -> None:
    for origin in (
        "verified_evidence",
        "trusted_internal",
        "knowledge",
        "memory",
        "tool_result",
        "model_generated",
        "user_data",
        "external_data",
        "external_untrusted",
        "unknown",
    ):
        with pytest.raises(ValidationError):
            TrustUnit(
                subject="unit",
                boundary="memory",
                origin=origin,  # type: ignore[arg-type]
                instruction_authority="policy",
            )


def test_authoritative_origins_may_carry_authority() -> None:
    system = TrustUnit(
        subject="policy",
        boundary="context_capsule",
        origin="system",
        instruction_authority="system",
    )
    policy = TrustUnit(
        subject="policy",
        boundary="context_capsule",
        origin="governed_policy",
        instruction_authority="policy",
    )
    assert system.instruction_authority == "system"
    assert policy.instruction_authority == "policy"


def test_trust_unit_round_trip_preserves_fields() -> None:
    unit = TrustUnit(
        subject="ctx://sha256/abc",
        boundary="context_capsule",
        origin="tool_result",
        trust_level="observed",
        taint=("tool_output",),
        provenance=("run:1",),
        freshness="fresh",
        evidence_refs=("evidence:x",),
    )
    loaded = TrustUnit.model_validate_json(unit.model_dump_json())
    assert loaded == unit


def test_tool_risk_profile_requires_a_class() -> None:
    with pytest.raises(ValidationError):
        ToolRiskProfile(tool="mystery", risk_classes=())


def test_permission_set_and_authorization_round_trip() -> None:
    grants = AgentPermissionSet(
        subject="critic",
        allowed_tools=("context_capsule",),
        allowed_risk_classes=("read_only",),
        denied_tools=("k6",),
    )
    auth = ToolAuthorization(
        subject="critic",
        tool="k6",
        decision="deny",
        risk_classes=("external_side_effect", "production_impact"),
        code="AF-TOOL-DENIED",
        field="tool",
        unlock="have a human remove the tool from the role's denied_tools",
    )
    assert grants.denied_tools == ("k6",)
    assert auth.decision == "deny"
    assert auth.code == "AF-TOOL-DENIED"


def test_gate_result_and_quarantine_round_trip() -> None:
    gate = MemoryGateResult(
        candidate_id="candidate:0123456789abcdef",
        verdict="quarantine",
        gates_passed=("scope", "origin", "evidence"),
        gates_failed=("trust",),
        quarantine_reasons=("trust candidate below policy minimum observed",),
        code="AF-MEMORY-TRUST-QUARANTINED",
        field="trust_level",
    )
    assert gate.verdict == "quarantine"
    row = MemoryQuarantine(
        quarantine_id="quarantine:0123456789abcdef",
        candidate_id="candidate:0123456789abcdef",
        memory_id="memory:0123456789abcdef",
        state="quarantined",
        reasons=("trust candidate below policy minimum observed",),
        created_at="2026-10-05T10:00:00Z",
    )
    loaded = MemoryQuarantine.model_validate_json(row.model_dump_json())
    assert loaded.state == "quarantined"
    assert loaded.verdict is None


def test_propagation_record_shape() -> None:
    derived = TrustUnit(
        subject="claim:1",
        boundary="memory",
        origin="external_untrusted",
        trust_level="untrusted",
        taint=("external", "untrusted"),
    )
    record = TrustPropagation(
        transform="parse_extract",
        derived=derived,
        derived_from=("web:page",),
        reason="parser extracted the claim verbatim",
    )
    assert record.taint_reduced is False
    assert record.derived.instruction_authority == "none"
