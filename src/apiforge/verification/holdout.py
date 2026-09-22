"""Apply allowlisted local mutations and verify that they are detected."""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.verification import HoldoutRecord
from apiforge.verification.service import verify_project

_REPLACEMENTS: dict[str, tuple[str, str]] = {
    "remove-auth": ("AUTH_REQUIRED = True", "AUTH_REQUIRED = False"),
    "remove-idempotency": (
        "IDEMPOTENCY_REQUIRED = True",
        "IDEMPOTENCY_REQUIRED = False",
    ),
    "bypass-cursor": ("CURSOR_VALIDATION = True", "CURSOR_VALIDATION = False"),
}


def _manifest(path: Path) -> list[dict[str, object]]:
    try:
        value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError("AF-HOLDOUT-MANIFEST", str(exc)) from exc
    mutations = value.get("mutations") if isinstance(value, dict) else None
    if not isinstance(mutations, list):
        raise ContractError("AF-HOLDOUT-MANIFEST", "mutations must be a list")
    return [item for item in mutations if isinstance(item, dict)]


def run_holdouts(
    root: Path,
    project: Path,
    contract: Path,
    manifest: Path,
) -> tuple[HoldoutRecord, ...]:
    records: list[HoldoutRecord] = []
    base = Path(root) / ".apiforge" / "holdouts"
    for item in _manifest(manifest):
        mutation_id = str(item.get("id", ""))
        expected = str(item.get("expected_detection", ""))
        if mutation_id not in _REPLACEMENTS or expected not in {"security", "idempotency", "pagination"}:
            raise ContractError("AF-HOLDOUT-MUTATION", f"unsupported mutation {mutation_id!r}")
        target = str(item.get("target", "app.py"))
        destination = base / mutation_id
        shutil.rmtree(destination, ignore_errors=True)
        shutil.copytree(project, destination)
        target_path = destination / target
        if not target_path.is_file():
            raise ContractError("AF-HOLDOUT-TARGET", f"missing mutation target {target}")
        old, new = _REPLACEMENTS[mutation_id]
        content = target_path.read_text(encoding="utf-8")
        if old not in content:
            raise ContractError("AF-HOLDOUT-TARGET", f"marker {old!r} absent from {target}")
        target_path.write_text(content.replace(old, new, 1), encoding="utf-8")
        checks = verify_project(contract, destination)
        detected = any(check.axis == expected and check.verdict == "fail" for check in checks)
        records.append(HoldoutRecord(
            mutation_id=mutation_id,
            target=target,
            expected_axis=expected,  # type: ignore[arg-type]
            detected=detected,
            evidence=(f"holdout:{mutation_id}",),
            limitation=None if detected else "mutation did not change the expected proof axis",
        ))
    return tuple(records)
