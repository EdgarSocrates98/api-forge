"""Dynatrace projection boundary; no credentials are read by the core."""

from collections.abc import Mapping
from typing import Literal

from apiforge.contracts.observability import Capability, OperationReceipt, VendorIntent


class DynatraceAdapter:
    name = "dynatrace"

    def capabilities(self) -> tuple[Capability, ...]:
        return (
            Capability(name="monitor", supported=True),
            Capability(name="slo", supported=True),
            Capability(name="dashboard", supported=True),
            Capability(
                name="apply",
                supported=False,
                read_only=False,
                reason="broker adapter not configured",
            ),
        )

    def project(self, intent: VendorIntent) -> Mapping[str, object]:
        return {"name": intent.name, "kind": intent.kind, "config": dict(intent.specification)}

    def apply(self, intent: VendorIntent, dry_run: bool = True) -> OperationReceipt:
        status: Literal["dry_run", "refused"] = "dry_run" if dry_run else "refused"
        reason = "offline projection" if dry_run else "credential broker required"
        return OperationReceipt(
            operation_id=f"op:{intent.id}",
            intent_id=intent.id,
            status=status,
            provider=self.name,
            reason=reason,
        )
