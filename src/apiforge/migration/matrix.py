"""Runtime version matrix resolution."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.compatibility import (
    CellState,
    CompatibilityCell,
    CompatibilityMatrix,
    RuntimeReceipt,
)
from apiforge.contracts.evidence import EvidenceRecord
from apiforge.core.ids import stable_id

_DEFAULT_MATRIX = (
    Path(__file__).resolve().parents[3] / "knowledge" / "runtime-migration" / "matrix.yaml"
)


def load_matrix(path: Path | None = None) -> dict[str, Any]:
    source = path or _DEFAULT_MATRIX
    try:
        document = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError("AF-MIGRATION-MATRIX", str(exc)) from exc
    if not isinstance(document, dict) or not isinstance(document.get("ecosystems"), dict):
        raise ContractError("AF-MIGRATION-MATRIX", "missing ecosystems mapping")
    return document


def resolve_versions(
    ecosystem: str, source: str, target: str, path: Path | None = None
) -> dict[str, Any]:
    matrix = load_matrix(path)
    entry = matrix["ecosystems"].get(ecosystem)
    if not isinstance(entry, dict):
        raise ContractError("AF-MIGRATION-ECOSYSTEM", f"unsupported ecosystem {ecosystem!r}")
    versions = tuple(str(item) for item in entry.get("versions", ()))
    missing = tuple(v for v in (source, target) if v not in versions)
    if missing:
        raise ContractError("AF-MIGRATION-VERSION", f"unsupported {ecosystem} versions: {missing}")
    source_index = versions.index(source)
    target_index = versions.index(target)
    lower, upper = sorted((source_index, target_index))
    return {
        "ecosystem": ecosystem,
        "source": source,
        "target": target,
        "versions": versions,
        "source_index": source_index,
        "target_index": target_index,
        "direction": "same"
        if source_index == target_index
        else "upgrade"
        if source_index < target_index
        else "downgrade",
        "intermediate": versions[lower : upper + 1],
        "metadata": {key: value for key, value in entry.items() if key != "versions"},
    }


def compatibility_matrix(
    ecosystem: str,
    receipts: tuple[RuntimeReceipt, ...] = (),
    path: Path | None = None,
) -> CompatibilityMatrix:
    """Publish observed cells and leave every unobserved version unresolved."""
    document = load_matrix(path)
    entry = document["ecosystems"].get(ecosystem)
    if not isinstance(entry, dict):
        raise ContractError("AF-MIGRATION-ECOSYSTEM", f"unsupported ecosystem {ecosystem!r}")
    versions = tuple(str(item) for item in entry.get("versions", ()))
    by_version: dict[str, list[RuntimeReceipt]] = {version: [] for version in versions}
    for receipt in receipts:
        if receipt.ecosystem != ecosystem or receipt.runtime_version not in by_version:
            raise ContractError(
                "AF-MIGRATION-RECEIPT",
                f"receipt {receipt.runtime_version!r} is not declared for {ecosystem!r}",
            )
        by_version[receipt.runtime_version].append(receipt)
    cells = tuple(
        CompatibilityCell(
            ecosystem=ecosystem,
            runtime_version=version,
            state=(
                "passed"
                if any(item.state == "passed" for item in by_version[version])
                else "failed"
                if by_version[version]
                else "unresolved"
            ),
            receipts=tuple(by_version[version]),
            limitations=() if by_version[version] else ("no execution receipt",),
        )
        for version in versions
    )
    return CompatibilityMatrix(
        ecosystem=ecosystem,
        cells=cells,
        observed_versions=tuple(cell.runtime_version for cell in cells if cell.receipts),
        unresolved_versions=tuple(
            cell.runtime_version for cell in cells if cell.state == "unresolved"
        ),
    )


def observe_python_interpreter(
    executable: str,
    *,
    environment: str,
    observed_at: str,
    timeout_seconds: int = 30,
) -> RuntimeReceipt:
    """Execute one allowlisted local Python interpreter and emit a receipt."""
    executable_name = Path(executable).name.lower()
    if not executable_name.startswith("python"):
        raise ContractError(
            "AF-MIGRATION-INTERPRETER",
            f"only Python executables are allowed, got {executable!r}",
        )
    command = (
        executable,
        "-c",
        "import sys; print('.'.join(str(item) for item in sys.version_info[:3]))",
    )
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError("AF-MIGRATION-INTERPRETER", str(exc)) from exc
    output = (completed.stdout + completed.stderr).strip()
    runtime_version = completed.stdout.strip().split(".", maxsplit=2)
    version = ".".join(runtime_version) if len(runtime_version) == 3 else "unknown"
    state: CellState = "passed" if completed.returncode == 0 and version != "unknown" else "failed"
    output_hash = hashlib.sha256(output.encode("utf-8")).hexdigest()
    receipt_ref = stable_id(
        "python-receipt",
        {"executable": executable, "environment": environment, "version": version},
    )
    return RuntimeReceipt(
        ecosystem="python",
        runtime_version=version,
        environment=environment,
        state=state,
        observed_at=observed_at,
        command=" ".join(command),
        receipt_ref=receipt_ref,
        output_hash=output_hash,
        evidence=EvidenceRecord(
            level="observed",
            source="allowlisted-local-interpreter",
            refs=(receipt_ref,),
            limitations=("local interpreter proof does not claim CI or production support",),
        ),
    )
