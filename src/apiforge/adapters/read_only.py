"""Local read-only data doubles for the verified API slice."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Protocol

from apiforge.contracts.base import ContractError


class ReadOnlyStore(Protocol):
    def get(self, key: str) -> Mapping[str, object] | None: ...

    def scan(self, prefix: str = "") -> tuple[Mapping[str, object], ...]: ...


class FixtureStore:
    """A deterministic store with no mutation methods by design."""

    def __init__(self, records: Mapping[str, Mapping[str, object]]) -> None:
        self._records = {str(key): dict(value) for key, value in records.items()}

    def get(self, key: str) -> Mapping[str, object] | None:
        value = self._records.get(key)
        return dict(value) if value is not None else None

    def scan(self, prefix: str = "") -> tuple[Mapping[str, object], ...]:
        return tuple(
            dict(value) for key, value in sorted(self._records.items()) if key.startswith(prefix)
        )


def load_fixture(path: Path) -> FixtureStore:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ContractError("AF-DATA-FIXTURE", f"cannot load {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError("AF-DATA-FIXTURE", "fixture must be a JSON object")
    return FixtureStore({str(key): value for key, value in data.items() if isinstance(value, dict)})
