"""Evidence-bound gRPC throughput and latency calculations."""

from __future__ import annotations

from apiforge.contracts.grpc import GrpcPerformanceReport, GrpcPerformanceRun


def evaluate(
    run: GrpcPerformanceRun, min_samples: int = 100, max_generator_saturation: float = 0.8
) -> GrpcPerformanceReport:
    rps = run.requests / run.duration_s
    valid = run.requests >= min_samples and (
        run.generator_saturation is None or run.generator_saturation <= max_generator_saturation
    )
    reason = None if valid else "insufficient samples or generator saturation"
    return GrpcPerformanceReport(rps=rps, tps=rps, valid=valid, reason=reason)
