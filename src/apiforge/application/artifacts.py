"""Load persisted API Forge artifact envelopes at application boundaries."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from apiforge.contracts.base import ContractError
from apiforge.core.models import Finding


def findings_from_payload(payload: object, *, source: str = "findings") -> tuple[Finding, ...]:
    """Validate a bare findings list or the official findings envelope."""
    raw: object = payload
    if isinstance(payload, Mapping):
        raw = payload.get("findings")
    if not isinstance(raw, list):
        raise ContractError(
            "AF-FINDINGS-ENVELOPE",
            f"{source}: expected a findings list or an object with a findings list",
        )
    try:
        return tuple(Finding.model_validate(item) for item in raw)
    except (TypeError, ValueError, ValidationError) as exc:
        raise ContractError("AF-FINDINGS-CONTRACT", f"{source}: invalid finding: {exc}") from exc


def load_findings(path: Path) -> tuple[Finding, ...]:
    """Read and validate an official findings artifact from disk."""
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError("AF-FINDINGS-INPUT", f"{path}: {exc}") from exc
    return findings_from_payload(payload, source=str(path))
