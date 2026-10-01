"""Code generation adapters; fake is deterministic and always available."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.grpc import (
    GrpcArtifact,
    GrpcCodegenRequest,
    GrpcCodegenResult,
    GrpcDiagnostic,
    GrpcIR,
    GrpcSeverity,
)
from apiforge.grpc.artifacts import artifact
from apiforge.grpc.capabilities import available


def generate(ir: GrpcIR, request: GrpcCodegenRequest) -> GrpcCodegenResult:
    if request.tool != "fake" and not available(request.tool):
        return GrpcCodegenResult(
            status="unsupported",
            diagnostics=(
                GrpcDiagnostic(
                    code="GRPC-TOOLCHAIN-MISSING",
                    severity=GrpcSeverity.REVIEW,
                    message=f"toolchain unavailable: {request.tool}",
                ),
            ),
        )
    root = Path(request.output_dir)
    root.mkdir(parents=True, exist_ok=True)
    artifacts: list[GrpcArtifact] = []
    for language in request.languages:
        extension = {"python": ".py", "go": ".go", "java": ".java"}[language]
        path = root / f"{ir.services[0].name if ir.services else 'api'}_grpc{extension}"
        path.write_text(
            f"generated_by=api-forge\nlanguage={language}\nsource={ir.source_sha256}\n",
            encoding="utf-8",
        )
        artifacts.append(artifact(path, language))
    return GrpcCodegenResult(status="generated", artifacts=tuple(artifacts))
