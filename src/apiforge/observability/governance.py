"""Safety boundary for plan, dry-run, approval and apply."""

from __future__ import annotations

from apiforge.contracts.observability import OperationReceipt, VendorIntent


def govern(intent: VendorIntent, approved: bool = False, dry_run: bool = True) -> OperationReceipt:
    if intent.risk == "external_mutation" and not approved:
        return OperationReceipt(
            operation_id=f"op:{intent.id}",
            intent_id=intent.id,
            status="refused",
            provider="control-plane",
            reason="human approval required",
        )
    if dry_run:
        return OperationReceipt(
            operation_id=f"op:{intent.id}",
            intent_id=intent.id,
            status="dry_run",
            provider="control-plane",
            evidence=("no external mutation performed",),
        )
    return OperationReceipt(
        operation_id=f"op:{intent.id}",
        intent_id=intent.id,
        status="planned",
        provider="control-plane",
        reason="provider adapter required",
    )
