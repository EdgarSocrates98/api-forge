"""Deterministic taint propagation (§10): unions, reductions, authority."""

from __future__ import annotations

import pytest

from apiforge.trust.plane import external_unit, trust_unit
from apiforge.trust.propagation import propagate


def test_propagation_unions_taint_and_takes_weakest_trust() -> None:
    verified = trust_unit("verified_evidence", subject="fact:1", boundary="memory")
    untrusted = external_unit("web", subject="web:page")
    record = propagate(
        (verified, untrusted),
        transform="parse_extract",
        subject="claim:1",
        boundary="memory",
    )
    derived = record.derived
    assert derived.trust_level == "untrusted"
    assert derived.origin == "external_untrusted"
    assert "external" in derived.taint and "untrusted" in derived.taint
    assert derived.instruction_authority == "none"
    assert record.taint_reduced is False


def test_verbatim_transform_never_cleans_taint() -> None:
    model = trust_unit("model_generated", subject="draft:1", boundary="memory")
    record = propagate((model,), transform="verbatim", subject="copy:1", boundary="blackboard")
    assert "model_generated" in record.derived.taint
    assert record.derived.trust_level == "candidate"


def test_governed_verification_reduces_taint_and_lifts_one_tier() -> None:
    untrusted = external_unit("web", subject="web:page")
    record = propagate(
        (untrusted,),
        transform="governed_verification",
        subject="claim:verified",
        boundary="memory",
        evidence_refs=("evidence:ci-run-42",),
        reason="independent CI run reproduced the claim",
    )
    derived = record.derived
    assert record.taint_reduced is True
    assert "untrusted" not in derived.taint and "external" not in derived.taint
    # one tier above untrusted (order 1) → observed (order 2); never a leap
    assert derived.trust_level == "observed"
    assert derived.instruction_authority == "none"
    assert derived.evidence_refs == ("evidence:ci-run-42",)


def test_verification_without_evidence_changes_nothing() -> None:
    untrusted = external_unit("web", subject="web:page")
    record = propagate(
        (untrusted,),
        transform="governed_verification",
        subject="claim:unverified",
        boundary="memory",
    )
    assert record.taint_reduced is False
    assert record.derived.trust_level == "untrusted"
    assert "untrusted" in record.derived.taint


def test_instruction_authority_never_widens_past_data() -> None:
    policy = trust_unit("governed_policy", subject="policy:1", boundary="context_capsule")
    data = trust_unit("tool_result", subject="out:1", boundary="tool_result")
    record = propagate(
        (policy, data),
        transform="system_synthesis",
        subject="merged:1",
        boundary="context_capsule",
    )
    # one data source in the mix → derived authority collapses to none
    assert record.derived.instruction_authority == "none"


def test_system_synthesis_over_authoritative_sources_keeps_weaker_authority() -> None:
    system = trust_unit("system", subject="sys:1", boundary="context_capsule")
    policy = trust_unit("governed_policy", subject="pol:1", boundary="context_capsule")
    record = propagate(
        (system, policy),
        transform="system_synthesis",
        subject="merged:1",
        boundary="context_capsule",
    )
    assert record.derived.instruction_authority == "policy"


def test_propagation_requires_sources() -> None:
    with pytest.raises(ValueError, match="AF-TRUST-PROPAGATION-EMPTY"):
        propagate((), transform="verbatim", subject="x")
