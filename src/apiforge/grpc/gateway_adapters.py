"""Gateway projection adapters with capability-aware offline output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apiforge.contracts.grpc import GrpcDiagnostic, GrpcGatewayProjection, GrpcIR, GrpcSeverity
from apiforge.grpc.artifacts import artifact


def project(ir: GrpcIR, gateway: str, output_dir: str) -> GrpcGatewayProjection:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    if gateway == "openapi":
        document: dict[str, Any] = {
            "openapi": "3.0.3",
            "info": {"title": ir.package or "gRPC API", "version": "1.0.0"},
            "paths": {},
        }
        for service in ir.services:
            for rpc in service.rpcs:
                if rpc.http_path:
                    document["paths"][rpc.http_path] = {
                        rpc.http_method or "post": {"operationId": rpc.full_name}
                    }
        path = root / "openapi.json"
        path.write_text(json.dumps(document, indent=2, sort_keys=True), encoding="utf-8")
        return GrpcGatewayProjection(
            gateway=gateway, status="projected", artifacts=(artifact(path, "openapi"),)
        )
    if gateway in {"envoy", "grpc_gateway", "grpc_web"}:
        path = root / f"{gateway}.yaml"
        path.write_text(
            f"gateway: {gateway}\nsource_sha256: {ir.source_sha256}\n", encoding="utf-8"
        )
        return GrpcGatewayProjection(
            gateway=gateway, status="projected", artifacts=(artifact(path, gateway),)
        )
    return GrpcGatewayProjection(
        gateway=gateway,
        status="unsupported",
        diagnostics=(
            GrpcDiagnostic(
                code="GRPC-GATEWAY-UNKNOWN",
                severity=GrpcSeverity.REVIEW,
                message=f"unknown gateway: {gateway}",
            ),
        ),
    )
