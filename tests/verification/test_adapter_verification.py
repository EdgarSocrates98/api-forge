from __future__ import annotations

from apiforge.contracts.adapter import AdapterExecution
from apiforge.contracts.sandbox import SandboxCommandResult
from apiforge.verification.adapter import verify_adapter_execution, verify_sandbox_result


def test_heuristic_adapter_is_not_reported_as_runtime_verified() -> None:
    check = verify_adapter_execution(
        AdapterExecution(adapter_id="rds", evidence_level="heuristic")
    )
    assert check.axis == "adapter"
    assert check.verdict == "inconclusive"


def test_unblocked_mutation_adapter_fails_security_boundary() -> None:
    check = verify_adapter_execution(
        AdapterExecution(adapter_id="aws", mode="live_mutation", status="completed")
    )
    assert check.axis == "security"
    assert check.verdict == "fail"


def test_sandbox_result_requires_evidence() -> None:
    check = verify_sandbox_result(
        SandboxCommandResult(status="passed", command=("python",), cwd=".", return_code=0)
    )
    assert check.verdict == "inconclusive"
