"""Final-convergence phase 6: TrustUnit admission inside role context.

Every context unit a role receives now carries an annotated TrustUnit:
capsule refs through ``annotate_ref``, run artifacts as ``model_generated``
first-party data — ``instruction_authority=none`` in both. The role policy's
``trust_floor`` and ``denied_taints`` gate admission; denied units are named
in ``plan.unresolved`` via ``AF-TRUST-*`` notes, never silently dropped.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from apiforge.context.role_policy import admit_refs, filter_refs
from apiforge.contracts.context import ContextRef
from apiforge.contracts.context_quality import RoleContextPolicy
from apiforge.runtime.role_context import plan_roles
from tests.context.gateway_support import analyzed_root


def _ref(seed: str, *, kind: str = "code", origin: str = "code") -> ContextRef:
    return ContextRef(
        uri=f"ctx://sha256/{hashlib.sha256(seed.encode()).hexdigest()}",
        kind=kind,  # type: ignore[arg-type]
        label=seed,
        source=f"{seed}.py",  # type: ignore[arg-type]
        size_bytes=10,
        provenance="test",
        origin=origin,  # type: ignore[arg-type]
    )


def test_admission_annotates_every_kept_ref() -> None:
    policy = RoleContextPolicy(role="specialist")
    refs = [_ref("a", kind="code", origin="code"), _ref("b", kind="contract", origin="contract")]
    kept, trimmed, notes, units = admit_refs(policy, refs)
    assert kept == refs and trimmed == [] and notes == []
    assert [unit.subject for unit in units] == [ref.uri for ref in refs]
    # trusted_internal / verified_evidence origins — data, never authority
    assert all(unit.instruction_authority == "none" for unit in units)


def test_trust_floor_denies_below_and_admits_above() -> None:
    policy = RoleContextPolicy(role="reviewer", trust_floor="verified")
    low = _ref("code-a", kind="code", origin="code")  # trusted_internal -> trusted
    high = _ref("spec-a", kind="contract", origin="contract")  # verified_evidence
    kept, trimmed, notes, units = admit_refs(policy, [low, high])
    assert kept == [high]
    assert trimmed == [low.uri]
    assert any(note.startswith("AF-TRUST-FLOOR") for note in notes)
    assert [unit.subject for unit in units] == [high.uri]


def test_denied_taints_trim_and_name_the_taint() -> None:
    policy = RoleContextPolicy(
        role="referee", denied_taints=("unverified_source", "prompt_injection")
    )
    knowledge = _ref("kb", kind="contract", origin="knowledge")  # taint: unverified_source
    graph = _ref("graph", kind="schema", origin="graph")
    kept, trimmed, notes, units = admit_refs(policy, [knowledge, graph])
    assert kept == [graph]
    assert trimmed == [knowledge.uri]
    assert any("AF-TRUST-TAINT-DENIED" in note for note in notes)
    assert all("unverified_source" not in unit.taint for unit in units)


def test_unknown_floor_never_silent() -> None:
    # an unrecognized floor value fails policy validation, not the filter
    with pytest.raises(ValueError):
        RoleContextPolicy(role="reviewer", trust_floor="bogus")  # type: ignore[arg-type]


def test_filter_refs_stays_backward_compatible() -> None:
    refs = [_ref("a", kind="code", origin="code")]
    kept, trimmed, notes = filter_refs(RoleContextPolicy(role="specialist"), refs)
    assert kept == refs and trimmed == [] and notes == []


def test_plan_roles_records_trust_units_and_artifact_taint_gate(tmp_path: Path) -> None:
    root = analyzed_root(tmp_path, "fastapi")
    spec = SimpleNamespace(
        inputs=("target=POST /payments",), outcome="make POST /payments idempotent"
    )
    roles = (("author", "specialist"), ("judge", "reviewer"))
    plan = plan_roles(
        root,
        spec,
        roles,
        context_bytes=32000,
        run_id="run-trust",
        artifacts={"author": "artifact-author-1"},
    )
    rows = {row.capability: row for row in plan.roles}
    reviewer = rows["judge"]
    # the run-produced artifact reaches the reviewer as model_generated data
    assert reviewer.artifact_refs == ("artifact:artifact-author-1",)
    artifact_units = [
        unit for unit in reviewer.trust_units if unit.subject == "artifact:artifact-author-1"
    ]
    assert len(artifact_units) == 1
    unit = artifact_units[0]
    assert unit.origin == "model_generated"
    assert unit.instruction_authority == "none"
    assert "model_generated" in unit.taint
    assert unit.provenance == ("run:run-trust",)
    # every admitted capsule ref carries its TrustUnit; verified_evidence and
    # trusted_internal origins are >= the reviewer's observed floor
    ref_subjects = {unit.subject for unit in reviewer.trust_units}
    assert set(reviewer.refs) <= ref_subjects
    assert all(unit.instruction_authority == "none" for unit in reviewer.trust_units), (
        "data never gains instruction authority"
    )


def test_shipped_policy_denies_dangerous_taints_on_every_role() -> None:
    from apiforge.runtime.role_context import load_role_policy

    policy = load_role_policy()
    for role in ("specialist", "reviewer", "critic", "referee"):
        row = policy["policies"][role]
        assert {"prompt_injection", "instruction_laundering", "malicious_artifact"} <= set(
            row.denied_taints
        )
