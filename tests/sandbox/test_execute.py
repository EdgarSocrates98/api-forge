from __future__ import annotations

import sys

import pytest

from apiforge.contracts.base import ContractError
from apiforge.contracts.sandbox import SandboxCommand
from apiforge.sandbox.execute import run_sandbox_command


def test_sandbox_runs_allowlisted_command_and_returns_evidence(tmp_path) -> None:
    result = run_sandbox_command(
        tmp_path,
        SandboxCommand(command=(sys.executable, "-c", "print('ok')"), cwd=str(tmp_path)),
        allowlist=frozenset({sys.executable}),
    )
    assert result.status == "passed"
    assert result.return_code == 0
    assert result.stdout.strip() == "ok"
    assert result.evidence_refs


def test_sandbox_blocks_non_allowlisted_command(tmp_path) -> None:
    result = run_sandbox_command(
        tmp_path, SandboxCommand(command=("not-allowed",), cwd=str(tmp_path))
    )
    assert result.status == "blocked"


def test_sandbox_rejects_cwd_escape(tmp_path) -> None:
    with pytest.raises(ContractError, match="AF-SANDBOX-CWD"):
        run_sandbox_command(
            tmp_path,
            SandboxCommand(command=(sys.executable, "-c", "pass"), cwd=str(tmp_path.parent)),
            allowlist=frozenset({sys.executable}),
        )
