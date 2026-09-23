"""Injected transports for read-only external integrations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol


class TransportError(RuntimeError):
    """A bounded failure from an external read-only transport."""

    def __init__(self, code: str, detail: str, *, retryable: bool = False) -> None:
        self.code = code
        self.retryable = retryable
        super().__init__(f"{code}: {detail}")


class ReadOnlyTransport(Protocol):
    """Only GET-like reads are exposed to provider adapters."""

    def get_json(self, path: str, *, params: Mapping[str, str] | None = None) -> object: ...
