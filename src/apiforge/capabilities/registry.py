"""Load the deterministic public capability matrix."""

from __future__ import annotations

from collections.abc import Mapping
from importlib import resources
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from apiforge.contracts.base import ContractError
from apiforge.contracts.platform import CapabilityRecord, VerticalCoverage


def _matrix_path() -> Path:
    return Path(str(resources.files("apiforge.rules").joinpath("capability_matrix.yaml")))


def _load_document(path: Path | None) -> Mapping[str, Any]:
    source = path or _matrix_path()
    try:
        value = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError("AF-CAPABILITY-MATRIX", f"{source}: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ContractError("AF-CAPABILITY-MATRIX", f"{source}: expected a mapping")
    return value


def load_capabilities(path: Path | None = None) -> tuple[CapabilityRecord, ...]:
    """Load and validate every public capability in deterministic order."""
    document = _load_document(path)
    raw = document.get("capabilities")
    if not isinstance(raw, Mapping):
        raise ContractError("AF-CAPABILITY-MATRIX", "missing capabilities mapping")
    records: list[CapabilityRecord] = []
    for capability_id, value in raw.items():
        if not isinstance(value, Mapping):
            raise ContractError("AF-CAPABILITY-MATRIX", f"{capability_id}: expected mapping")
        try:
            records.append(
                CapabilityRecord.model_validate(
                    {"capability_id": str(capability_id), **dict(value)}
                )
            )
        except (TypeError, ValueError, ValidationError) as exc:
            raise ContractError("AF-CAPABILITY-CONTRACT", f"{capability_id}: {exc}") from exc
    return tuple(sorted(records, key=lambda item: item.capability_id))


def load_vertical_coverage(path: Path | None = None) -> tuple[VerticalCoverage, ...]:
    """Load the fixture/golden/holdout declarations from the matrix."""
    document = _load_document(path)
    raw = document.get("verticals")
    if not isinstance(raw, list):
        raise ContractError("AF-CAPABILITY-MATRIX", "missing verticals list")
    try:
        return tuple(
            VerticalCoverage.model_validate(item) for item in raw if isinstance(item, Mapping)
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise ContractError("AF-CAPABILITY-CONTRACT", f"invalid vertical coverage: {exc}") from exc
