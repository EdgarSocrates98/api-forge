"""Independent offline verification for gRPC control-plane outcomes."""

from __future__ import annotations

from typing import Literal

from apiforge.contracts.grpc import (
    GrpcCodegenResult,
    GrpcCompatibilityReport,
    GrpcIR,
    GrpcVerification,
)


def verify(
    ir: GrpcIR,
    compatibility: GrpcCompatibilityReport | None = None,
    codegen: GrpcCodegenResult | None = None,
) -> GrpcVerification:
    checks = ["ir-present", "source-hash", "stream-modes-bounded"]
    gaps: list[str] = []
    if not ir.services:
        gaps.append("no services discovered")
    if ir.unresolved:
        gaps.extend(ir.unresolved)
    if compatibility and compatibility.verdict == "breaking":
        gaps.append("breaking compatibility findings")
    if codegen and codegen.status in {"unsupported", "failed", "blocked"}:
        gaps.append(f"codegen:{codegen.status}")
    verdict: Literal["DONE", "REVIEW", "BLOCKED"] = "DONE" if not gaps else "REVIEW"
    return GrpcVerification(
        verdict=verdict,
        checks=tuple(checks),
        gaps=tuple(sorted(set(gaps))),
        evidence=(f"source:{ir.source_sha256}",),
    )


def verify_holdout(expected_digest: str, actual_ir: GrpcIR) -> GrpcVerification:
    detected = actual_ir.source_sha256 != expected_digest
    return GrpcVerification(verdict="REVIEW" if detected else "DONE", checks=("holdout-digest",), gaps=("holdout mutation detected",) if detected else (), evidence=(f"source:{actual_ir.source_sha256}",))
