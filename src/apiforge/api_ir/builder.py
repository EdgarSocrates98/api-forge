"""Compose the canonical API-IR from a contract and a code inventory.

Zero, one, or many projections per side are preserved — duplicate contract
operations or duplicate code routes are never collapsed. Ordering is fully
deterministic: projections sort by source path/line and operations by
path/method.
"""

from __future__ import annotations

import apiforge
from apiforge.adapters.inventory import CodeInventory
from apiforge.api_ir.models import ApiModel, ApiOperation, Projection
from apiforge.core.models import Diagnostic
from apiforge.openapi.models import OpenApiDocument


def _projection_key(item: Projection) -> tuple[str, int, str]:
    return (item.source.path, item.source.line or 0, item.fact_id)


def _diagnostic_key(item: Diagnostic) -> tuple[str, str, int, str]:
    source = item.source
    return (
        item.code,
        source.path if source else "",
        source.line if source and source.line else 0,
        item.message,
    )


def build_api_model(contract: OpenApiDocument, inventory: CodeInventory) -> ApiModel:
    """Merge contract operations and code route facts into one ApiModel."""
    operations: dict[tuple[str, str], dict[str, list[Projection]]] = {}

    def slot(method: str, path: str) -> dict[str, list[Projection]]:
        return operations.setdefault((method, path), {"contract": [], "code": []})

    for op in contract.operations:
        slot(op.method, op.path)["contract"].append(
            Projection(
                source_kind="contract",
                fact_id=op.fact_id,
                source=op.source,
                detail={"operation_id": op.operation_id, "raw": dict(op.raw)},
            )
        )
    for fact in inventory.facts:
        if fact.kind != "code.route":
            continue
        method = str(fact.measures["method"])
        path = str(fact.measures["path"])
        slot(method, path)["code"].append(
            Projection(
                source_kind="code",
                fact_id=fact.fact_id,
                source=fact.source,
                detail=dict(fact.attrs),
            )
        )

    ordered = [
        ApiOperation(
            method=method,
            path=path,
            contract_projections=tuple(sorted(projections["contract"], key=_projection_key)),
            code_projections=tuple(sorted(projections["code"], key=_projection_key)),
        )
        for (method, path), projections in operations.items()
    ]
    ordered.sort(key=lambda op: (op.path, op.method))

    input_hashes = {f"contract:{contract.source_path}": contract.sha256}
    input_hashes.update({f"code:{rel}": digest for rel, digest in inventory.input_hashes.items()})

    diagnostics = tuple(
        sorted(
            (*contract.diagnostics, *inventory.diagnostics),
            key=_diagnostic_key,
        )
    )
    return ApiModel(
        generator=f"apiforge {apiforge.__version__}",
        input_hashes=input_hashes,
        operations=tuple(ordered),
        diagnostics=diagnostics,
    )
