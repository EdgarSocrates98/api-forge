"""Independent verification for the local Commerce Orders slice."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.verification import (
    HoldoutRecord,
    ProofAxis,
    ProofVerdict,
    VerificationCheck,
    VerificationRecord,
)
from apiforge.taskspec import store
from apiforge.taskspec.planner import load_plan

_REQUIRED_PATHS = {
    "/v1/orders",
    "/v1/orders/{order_id}",
    "/v1/orders/{order_id}/cancel",
}


def _evidence(path: Path) -> str:
    return f"file:{path.as_posix()}#{hashlib.sha256(path.read_bytes()).hexdigest()[:16]}"


def _check(
    check_id: str,
    axis: ProofAxis,
    passed: bool,
    evidence: tuple[str, ...],
    gap: str,
) -> VerificationCheck:
    return VerificationCheck(
        check_id=check_id,
        axis=axis,
        verdict="pass" if passed else "fail",
        evidence=evidence if passed else (),
        gaps=() if passed else (gap,),
    )


def verify_project(contract: Path, project: Path) -> tuple[VerificationCheck, ...]:
    """Verify declared proof axes from local files, without executing the target."""
    contract_path = Path(contract)
    project_path = Path(project)
    app_path = project_path / "app.py"
    if not contract_path.is_file() or not app_path.is_file():
        missing = str(contract_path if not contract_path.is_file() else app_path)
        return tuple(
            VerificationCheck(
                check_id="inputs-present",
                axis="contract",
                verdict="inconclusive",
                gaps=(f"missing input: {missing}",),
            )
            for _ in (0,)
        )
    try:
        document: dict[str, Any] = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return (VerificationCheck(
            check_id="contract-parse",
            axis="contract",
            verdict="inconclusive",
            gaps=(f"contract parse failed: {exc}",),
        ),)
    app = app_path.read_text(encoding="utf-8")
    paths = set(document.get("paths", {})) if isinstance(document, dict) else set()
    checks = (
        _check(
            "contract-surface",
            "contract",
            _REQUIRED_PATHS.issubset(paths),
            (_evidence(contract_path),),
            "required order paths are absent from contract",
        ),
        _check(
            "operation-security",
            "security",
            bool(document.get("security")) and "AUTH_REQUIRED = True" in app,
            (_evidence(contract_path), _evidence(app_path)),
            "authentication requirement is absent or disabled",
        ),
        _check(
            "idempotency",
            "idempotency",
            "Idempotency-Key" in app and "IDEMPOTENCY_REQUIRED = True" in app,
            (_evidence(contract_path), _evidence(app_path)),
            "idempotency protection is absent or disabled",
        ),
        _check(
            "cursor-pagination",
            "pagination",
            "cursor" in app.lower() and "CURSOR_VALIDATION = True" in app,
            (_evidence(contract_path), _evidence(app_path)),
            "cursor pagination validation is absent or disabled",
        ),
    )
    return checks


def _aggregate(
    checks: tuple[VerificationCheck, ...], holdout: tuple[HoldoutRecord, ...]
) -> ProofVerdict:
    if not checks or any(check.verdict == "inconclusive" for check in checks):
        return "inconclusive"
    if any(check.verdict == "fail" for check in checks):
        return "fail"
    if not holdout or not all(item.detected for item in holdout):
        return "inconclusive"
    return "pass"


def verify_task(
    root: Path,
    task_id: str,
    *,
    project: Path,
    contract: Path,
    run_id: str = "manual",
    holdout: tuple[HoldoutRecord, ...] = (),
    verified_by: str = "af-verifier",
) -> VerificationRecord:
    """Verify a task from sealed artifacts and persist the independent record."""
    spec = store.load(root, task_id)
    plan = load_plan(root, task_id)
    if plan.revision != spec.revision:
        raise ContractError("AF-TASK-PLAN-STALE", "plan revision differs from task revision")
    checks = verify_project(contract, project)
    verdict = _aggregate(checks, holdout)
    gaps = tuple(sorted({gap for check in checks for gap in check.gaps}))
    if holdout and not all(item.detected for item in holdout):
        gaps += ("one or more declared holdouts were not detected",)
    record = VerificationRecord(
        task_id=task_id,
        revision=spec.revision,
        run_id=run_id,
        verdict=verdict,
        checks=checks,
        evidence=tuple(sorted({item for check in checks for item in check.evidence})),
        gaps=gaps,
        holdout=holdout,
        verified_by=verified_by,
    )
    path = store.task_dir(root, task_id) / "verification.json"
    path.write_text(json.dumps(record.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8")
    store.record_event(root, task_id, {
        "event": "verified",
        "revision": spec.revision,
        "run_id": run_id,
        "verdict": verdict,
        "verification": str(path),
    })
    return record


def load_verification(root: Path, task_id: str) -> VerificationRecord:
    path = store.task_dir(root, task_id) / "verification.json"
    if not path.is_file():
        raise ContractError("AF-VERIFY-MISSING", f"no verification for task {task_id!r}")
    return VerificationRecord.model_validate(json.loads(path.read_text(encoding="utf-8")))
