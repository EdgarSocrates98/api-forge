"""Adapter protocols and capability boundary."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Protocol

from apiforge.contracts.observability import (
    Capability,
    OperationReceipt,
    VendorIntent,
)


class SourceAdapter(Protocol):
    name: str

    def read(self, path: Path) -> Iterable[Mapping[str, object]]: ...


class VendorAdapter(Protocol):
    name: str

    def capabilities(self) -> tuple[Capability, ...]: ...

    def project(self, intent: VendorIntent) -> Mapping[str, object]: ...

    def apply(self, intent: VendorIntent, dry_run: bool = True) -> OperationReceipt: ...


class CredentialBroker(Protocol):
    def resolve(self, provider: str, reference: str) -> Mapping[str, str]: ...


def adapter_names() -> tuple[str, ...]:
    return ("otel-json", "runtime", "datadog", "dynatrace", "aws", "kubernetes", "vm")
