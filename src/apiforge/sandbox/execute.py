"""Allowlisted local process execution inside a copied sandbox tree."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.sandbox import SandboxCommand, SandboxCommandResult
from apiforge.core.ids import stable_id
from apiforge.runtime.store import content_hash

_DEFAULT_ALLOWLIST = frozenset({"python", "python.exe", "pytest", "pytest.exe", "java", "java.exe", "go", "go.exe"})


def _inside(root: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def run_sandbox_command(
    root: Path,
    request: SandboxCommand,
    *,
    allowlist: frozenset[str] = _DEFAULT_ALLOWLIST,
) -> SandboxCommandResult:
    """Run one allowlisted argv in ``root`` and return bounded evidence."""

    sandbox_root = Path(root).resolve()
    cwd = Path(request.cwd).resolve()
    if not _inside(sandbox_root, cwd):
        raise ContractError("AF-SANDBOX-CWD", "command cwd escapes sandbox root")
    executable = Path(request.command[0]).name.lower()
    allowed_names = {Path(item).name.lower() for item in allowlist}
    if executable not in allowed_names:
        return SandboxCommandResult(
            status="blocked",
            command=request.command,
            cwd=str(cwd),
            limitations=(f"executable not allowlisted: {executable}",),
        )
    limitation = "network policy is host-dependent unless the host enforces OS isolation"
    env = {"PATH": os.environ.get("PATH", "")}
    env.update(dict(request.environment))
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            list(request.command), cwd=cwd, env=env, capture_output=True,
            text=True, timeout=request.timeout_seconds, check=False, shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = int((time.perf_counter() - started) * 1000)
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        return SandboxCommandResult(
            status="timed_out", command=request.command, cwd=str(cwd),
            stdout=stdout[-20000:], stderr=stderr[-20000:], duration_ms=elapsed,
            evidence_refs=(f"sandbox:{stable_id('command', request.model_dump(mode='json'))}",),
            limitations=(limitation,),
        )
    elapsed = int((time.perf_counter() - started) * 1000)
    stdout = completed.stdout[-20000:]
    stderr = completed.stderr[-20000:]
    digest = content_hash({"command": request.command, "cwd": str(cwd), "return_code": completed.returncode, "stdout": stdout, "stderr": stderr})
    return SandboxCommandResult(
        status="passed" if completed.returncode == 0 else "failed",
        command=request.command, cwd=str(cwd), return_code=completed.returncode,
        stdout=stdout, stderr=stderr, duration_ms=elapsed,
        evidence_refs=(f"sandbox:{digest}",), limitations=(limitation,),
    )
