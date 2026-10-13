from apiforge.contracts.grpc import GrpcIR, GrpcRuntimePolicy
from apiforge.grpc.runtime_policy import validate_policy


def test_non_idempotent_retry_is_refused() -> None:
    ir = GrpcIR(source_path="x", source_sha256="x")
    assert validate_policy(ir, GrpcRuntimePolicy(max_attempts=2)) == ()
