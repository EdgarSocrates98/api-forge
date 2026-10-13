"""Cache and delta refusals: cataloged AF codes carrying the refused field and unlock."""

from __future__ import annotations

from apiforge.contracts.base import ContractError


class CacheError(ContractError):
    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        super().__init__(code, detail)
        self.field = field
        self.unlock = unlock


__all__ = ["CacheError"]
