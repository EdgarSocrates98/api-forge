import pytest
from pydantic import ValidationError

from apiforge.contracts.context import (
    CapsuleBudget,
    CapsuleRefusal,
    ContextCapsule,
    ContextRef,
    ContextScope,
)
from apiforge.contracts.economy import CostVector, RunLedgerEntry
from apiforge.contracts.registry import CONTRACTS

URI = "ctx://sha256/" + "a" * 64


def _ref(uri: str = URI) -> ContextRef:
    return ContextRef(
        uri=uri,
        kind="schema",
        label="schema:Order",
        source="openapi.yaml",
        size_bytes=10,
        provenance="schema-ref:Order",
        origin="contract",
    )


def test_registry_exposes_gateway_and_economy_contracts() -> None:
    for name in (
        "ContextRef/v1",
        "ContextCapsule/v1",
        "CapsuleBudget/v1",
        "CapsuleRefusal/v1",
        "CostVector/v1",
        "LedgerRef/v1",
        "RunLedgerEntry/v1",
    ):
        assert name in CONTRACTS


def test_context_ref_rejects_non_ctx_uri() -> None:
    with pytest.raises(ValidationError):
        _ref("ctx://schema/Order")


def test_capsule_rejects_duplicate_refs() -> None:
    with pytest.raises(ValidationError, match="unique"):
        ContextCapsule(
            capsule_id=URI,
            run_id="run-1",
            intent={"action": "inspect", "target": "POST /orders"},
            scope=ContextScope(scope="target", root=".", target="POST /orders"),
            refs=(_ref(), _ref()),
            budget=CapsuleBudget(context_bytes=1000),
        )


def test_refusal_requires_af_code() -> None:
    with pytest.raises(ValidationError):
        CapsuleRefusal(code="budget", field="budget_bytes", unlock="raise it")


def test_run_ledger_entry_keeps_tokens_unresolved_by_default() -> None:
    entry = RunLedgerEntry(run_id="run-1", verb="context capsule", source="contract")
    assert entry.cost == CostVector()
    assert entry.cost.observed_tokens is None
    assert entry.schema == "apiforge/run-ledger-entry/v1"
