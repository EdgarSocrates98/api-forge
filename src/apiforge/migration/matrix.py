"""Runtime version matrix resolution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError

_DEFAULT_MATRIX = Path(__file__).resolve().parents[3] / "knowledge" / "runtime-migration" / "matrix.yaml"


def load_matrix(path: Path | None = None) -> dict[str, Any]:
    source = path or _DEFAULT_MATRIX
    try:
        document = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError("AF-MIGRATION-MATRIX", str(exc)) from exc
    if not isinstance(document, dict) or not isinstance(document.get("ecosystems"), dict):
        raise ContractError("AF-MIGRATION-MATRIX", "missing ecosystems mapping")
    return document


def resolve_versions(ecosystem: str, source: str, target: str, path: Path | None = None) -> dict[str, Any]:
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
        "direction": "same" if source_index == target_index else "upgrade" if source_index < target_index else "downgrade",
        "intermediate": versions[lower : upper + 1],
        "metadata": {key: value for key, value in entry.items() if key != "versions"},
    }
