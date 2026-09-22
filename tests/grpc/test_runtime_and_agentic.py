from pathlib import Path

from apiforge.contracts.grpc import GrpcRuntimePolicy
from apiforge.contracts.task import TaskRisk
from apiforge.grpc.observability import normalize_otel_records
from apiforge.grpc.plan import compile_task_spec
from apiforge.grpc.runtime_policy import evaluate_deadline, runtime_capabilities
from apiforge.grpc.security import authorize_mutation
from apiforge.grpc.source import load_source
from apiforge.grpc.verify import verify_holdout


def test_runtime_and_agentic_gates_are_evidence_bound() -> None:
    ir = load_source(Path("tests/fixtures/grpc/orders.proto"))
    task = compile_task_spec("evolve grpc contract", ir, TaskRisk.READ_ONLY)
    assert task.acceptance_criteria and task.expected_proofs
    assert evaluate_deadline(6000, GrpcRuntimePolicy())["status"] == "DEADLINE_EXCEEDED"
    assert runtime_capabilities(GrpcRuntimePolicy())["health_check"] is True
    assert authorize_mutation(False, False).safe is False
    assert verify_holdout("different", ir).verdict == "REVIEW"
    assert normalize_otel_records([{"service": "orders", "rpc.method": "GetOrder", "trace_id": "t1"}])[0]["correlation_id"] == "t1"
