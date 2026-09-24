from pathlib import Path

from apiforge.contracts.compatibility import RuntimeReceipt
from apiforge.migration.matrix import compatibility_matrix, observe_python_interpreter


def test_matrix_publishes_only_observed_python_cells() -> None:
    receipt = RuntimeReceipt(
        ecosystem="python",
        runtime_version="3.12",
        environment="local",
        state="passed",
        observed_at="2026-09-23T00:00:00Z",
        command="pytest -q",
        receipt_ref="receipt:python:3.12",
    )
    matrix = compatibility_matrix(
        "python", (receipt,), Path("knowledge/runtime-migration/matrix.yaml")
    )
    cell = next(item for item in matrix.cells if item.runtime_version == "3.12")
    assert cell.state == "passed"
    assert "3.12" in matrix.observed_versions
    assert "3.13" in matrix.unresolved_versions


def test_local_probe_records_two_observed_interpreter_cells() -> None:
    import shutil
    import sys

    baseline = observe_python_interpreter(
        sys.executable,
        environment="venv-baseline",
        observed_at="2026-09-23T00:00:00Z",
    )
    alternate_executable = shutil.which("python") or sys.executable
    alternate = observe_python_interpreter(
        alternate_executable,
        environment="host-python",
        observed_at="2026-09-23T00:00:00Z",
    )
    assert baseline.state == alternate.state == "passed"
    assert baseline.runtime_version != "unknown"
    assert alternate.runtime_version != "unknown"
