"""Minimum Sufficient Context: deterministic prune, gate regressions, honesty."""

from __future__ import annotations

import hashlib

from apiforge.context.sufficiency import minimum_sufficient
from apiforge.contracts.context import ContextRef
from apiforge.contracts.context_quality import ContextUseRecord


def _uri(seed: str) -> str:
    return f"ctx://sha256/{hashlib.sha256(seed.encode()).hexdigest()}"


def _ref(seed: str, *, kind: str = "code", size: int = 100, origin: str = "code") -> ContextRef:
    return ContextRef(
        uri=_uri(seed),
        kind=kind,
        label=seed,
        source=f"{seed}.py",  # type: ignore[arg-type]
        size_bytes=size,
        provenance="test",
        origin=origin,  # type: ignore[arg-type]
    )


def _use(ref: ContextRef, action: str = "expanded", seq: int = 0) -> ContextUseRecord:
    return ContextUseRecord(
        use_id=f"r:{seq}",
        run_id="r",
        ref_uri=ref.uri,
        action=action,  # type: ignore[arg-type]
        bytes=ref.size_bytes,
    )


def test_unused_non_evidence_ref_is_pruned() -> None:
    contract = _ref("contract", kind="contract", origin="contract")
    unused_schema = _ref("schema", kind="schema", origin="contract")
    unused_code = _ref("noise", kind="code")
    refs = (contract, unused_schema, unused_code)
    uses = (_use(contract),)
    result = minimum_sufficient(refs, uses, run_id="r")
    assert result.sufficient
    assert result.pruned_refs == (unused_code.uri,)
    assert result.pruned_bytes == 100
    # evidence kinds are retained even when unused under the strict gate
    assert unused_schema.uri in result.kept_refs


def test_permissive_gate_prunes_unused_evidence() -> None:
    contract = _ref("contract", kind="contract", origin="contract")
    unused_schema = _ref("schema", kind="schema", origin="contract")
    refs = (contract, unused_schema)
    uses = (_use(contract),)
    result = minimum_sufficient(refs, uses, run_id="r", gate="permissive")
    assert result.pruned_refs == (unused_schema.uri,)


def test_missing_required_ref_blocks_sufficiency() -> None:
    ref = _ref("a", kind="contract", origin="contract")
    dead = _uri("never-in-capsule")
    result = minimum_sufficient((ref,), (_use(ref),), run_id="r", required_uris=[dead])
    assert not result.sufficient
    assert any("required" in note for note in result.unresolved)


def test_consumed_refs_are_never_pruned() -> None:
    cited = _ref("cited", kind="code")
    loaded_only = _ref("loaded", kind="code")
    refs = (cited, loaded_only)
    uses = (_use(cited, "cited"), _use(loaded_only, "assigned"))
    result = minimum_sufficient(refs, uses, run_id="r", gate="permissive")
    assert result.kept_refs == (cited.uri,)
    assert result.pruned_refs == (loaded_only.uri,)


def test_evidence_recall_regression_vetoes_permissive_only_by_note() -> None:
    contract = _ref("contract", kind="contract", origin="contract")
    schema = _ref("schema", kind="schema", origin="contract")
    code = _ref("handler", kind="code")
    refs = (contract, schema, code)
    uses = (_use(contract), _use(schema), _use(code))
    result = minimum_sufficient(refs, uses, run_id="r")
    # nothing unused -> nothing pruned; still honest about being already minimal
    assert not result.pruned_refs
    assert any("already minimal" in note for note in result.unresolved)


def test_quality_snapshot_both_sides() -> None:
    contract = _ref("contract", kind="contract", origin="contract")
    noise = _ref("noise", kind="code", size=500)
    result = minimum_sufficient(
        (contract, noise), (_use(contract),), run_id="r", required_uris=[contract.uri]
    )
    names = {metric.name for metric in result.metrics_before}
    assert names == {metric.name for metric in result.metrics_after}
    before = {m.name: m for m in result.metrics_before}
    after = {m.name: m for m in result.metrics_after}
    assert after["context_precision"].value > before["context_precision"].value
    assert result.sufficient
