"""Allowlisted local runtime probes for the six platform verticals."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.platform import PlatformRuntimeReceipt, VerticalRuntimeReceipt

VERTICALS = ("api", "database", "messaging", "cicd", "cloud", "frontend")


class PlatformRuntimeError(ContractError):
    """Actionable refusal from the allowlisted runtime probe boundary."""

    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        self.field = field
        self.unlock = unlock
        super().__init__(code, detail)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _probe(vertical: str, fixture: Path, observed_at: str) -> VerticalRuntimeReceipt:
    probe = fixture / "runtime_probe.py"
    if not probe.is_file():
        return VerticalRuntimeReceipt(
            vertical=vertical,
            fixture=str(fixture),
            probe=str(probe),
            probe_sha256="0" * 64,
            observed_at=observed_at,
            status="unresolved",
            limitations=("runtime probe is missing",),
        )
    try:
        completed = subprocess.run(
            [sys.executable, str(probe)],
            cwd=fixture,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return VerticalRuntimeReceipt(
            vertical=vertical,
            fixture=str(fixture),
            probe=str(probe),
            probe_sha256=_sha256(probe),
            observed_at=observed_at,
            status="failed",
            limitations=(f"probe execution failed: {exc}",),
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {}
    checks = payload.get("checks", []) if isinstance(payload, dict) else []
    limitations = payload.get("limitations", []) if isinstance(payload, dict) else []
    passed = (
        completed.returncode == 0
        and isinstance(payload, dict)
        and payload.get("status") == "passed"
    )
    return VerticalRuntimeReceipt(
        vertical=vertical,
        fixture=str(fixture),
        probe=str(probe),
        probe_sha256=_sha256(probe),
        observed_at=observed_at,
        status="passed" if passed else "failed",
        checks=tuple(str(item) for item in checks if isinstance(item, str)),
        limitations=tuple(str(item) for item in limitations if isinstance(item, str))
        + (() if passed else (completed.stderr.strip() or "probe returned a non-zero result",)),
    )


def verify_platform_runtime(
    root: Path,
    *,
    verticals: tuple[str, ...] = VERTICALS,
    now: str | None = None,
) -> PlatformRuntimeReceipt:
    """Execute only committed vertical probes and return a hash-bound receipt."""
    observed_at = now or datetime.now(UTC).isoformat()
    invalid = tuple(item for item in verticals if item not in VERTICALS)
    if invalid:
        raise PlatformRuntimeError(
            "AF-PLATFORM-VERTICAL",
            f"unsupported verticals: {invalid}",
            field="vertical",
            unlock="choose one of api, database, messaging, cicd, cloud or frontend",
        )
    base = root.resolve()
    results = tuple(
        _probe(item, base / "tests" / "fixtures" / "platform" / item, observed_at)
        for item in verticals
    )
    return PlatformRuntimeReceipt(observed_at=observed_at, verticals=results)


def runtime_summary(receipt: PlatformRuntimeReceipt) -> dict[str, Any]:
    return {
        "schema_version": receipt.schema_version,
        "observed_at": receipt.observed_at,
        "ok": bool(receipt.verticals)
        and all(item.status == "passed" for item in receipt.verticals),
        "passed": tuple(item.vertical for item in receipt.verticals if item.status == "passed"),
        "failed": tuple(item.vertical for item in receipt.verticals if item.status == "failed"),
        "unresolved": tuple(
            item.vertical for item in receipt.verticals if item.status == "unresolved"
        ),
    }
