from apiforge.contracts.grpc import GrpcPerformanceRun
from apiforge.grpc.performance import evaluate


def test_performance_preserves_invalid_evidence() -> None:
    result = evaluate(GrpcPerformanceRun(requests=2, duration_s=1, concurrency=1), min_samples=100)
    assert result.valid is False
    assert result.reason
