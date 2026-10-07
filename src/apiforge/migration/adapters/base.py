"""Common adapter protocol; adapters describe commands but never execute them."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from apiforge.migration.contracts import MigrationFinding, RuntimeCapability


@dataclass(frozen=True)
class AdapterObservation:
    files: tuple[str, ...]
    capabilities: tuple[RuntimeCapability, ...]
    findings: tuple[MigrationFinding, ...]


class RuntimeAdapter(Protocol):
    ecosystem: str

    def can_handle(self, source: str, target: str) -> bool: ...

    def discover(self, root: Path, source: str, target: str) -> AdapterObservation: ...

    def commands(self, root: Path) -> tuple[tuple[str, ...], ...]: ...
