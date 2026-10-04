"""Trust-unit annotation across capsule refs and external boundaries (§9)."""

from __future__ import annotations

from apiforge.contracts.context import ContextRef
from apiforge.trust.plane import (
    annotate_capsule,
    annotate_ref,
    external_unit,
    trust_unit,
)


def _ref(digest: str, origin: str, kind: str = "code") -> ContextRef:
    return ContextRef(
        uri=f"ctx://sha256/{digest}",
        kind=kind,  # type: ignore[arg-type]
        label=digest[:8],
        source="unit-test",
        size_bytes=10,
        provenance="unit-test",
        origin=origin,  # type: ignore[arg-type]
    )


def test_trust_unit_annotates_origin_baseline() -> None:
    unit = trust_unit("external_untrusted", subject="web:page", boundary="web")
    assert unit.trust_level == "untrusted"
    assert "untrusted" in unit.taint
    assert unit.instruction_authority == "none"

    trusted = trust_unit("verified_evidence", subject="fact:1", boundary="memory")
    assert trusted.trust_level == "verified"
    assert trusted.taint == ()

    system = trust_unit("system", subject="policy", boundary="context_capsule")
    assert system.instruction_authority == "system"


def test_annotate_ref_maps_capsule_origins() -> None:
    digest = "a" * 64
    assert annotate_ref(_ref(digest, "code")).trust.origin == "trusted_internal"
    assert annotate_ref(_ref(digest, "contract", "contract")).trust.origin == ("verified_evidence")
    assert annotate_ref(_ref(digest, "graph")).trust.origin == "verified_evidence"
    assert annotate_ref(_ref(digest, "knowledge", "knowledge")).trust.origin == "knowledge"
    assert annotate_ref(_ref(digest, "filesystem")).trust.origin == "trusted_internal"


def test_external_units_cover_every_boundary() -> None:
    for boundary, origin in (
        ("api_spec", "external_data"),
        ("log", "external_data"),
        ("ci_output", "external_data"),
        ("documentation", "external_data"),
        ("web", "external_untrusted"),
        ("mcp_response", "tool_result"),
        ("agent_handoff", "model_generated"),
    ):
        unit = external_unit(boundary, subject=f"{boundary}:x")  # type: ignore[arg-type]
        assert unit.origin == origin
        assert unit.instruction_authority == "none"


def test_annotate_capsule_preserves_ref_identity() -> None:
    from apiforge.contracts.context import (
        CapsuleBudget,
        ContextCapsule,
        ContextScope,
    )

    capsule = ContextCapsule(
        capsule_id="ctx://sha256/" + "c" * 64,
        run_id="run-1",
        intent={"verb": "check"},
        scope=ContextScope(root="."),
        refs=(
            _ref("a" * 64, "code"),
            _ref("b" * 64, "contract", "contract"),
        ),
        budget=CapsuleBudget(context_bytes=1024),
    )
    trusted = annotate_capsule(capsule)
    assert len(trusted) == 2
    assert trusted[0].ref.uri == "ctx://sha256/" + "a" * 64
    assert trusted[1].trust.trust_level == "verified"
