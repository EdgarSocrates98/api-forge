"""Governed errors for the API/Git/CI change-control application."""

from __future__ import annotations


class ChangeControlError(ValueError):
    """A change-control refusal with code, field and an explicit unlock."""

    def __init__(
        self,
        code: str,
        detail: str,
        *,
        field: str = "change-control",
        unlock: str = "inspect the documented contract and rerun the verifier",
    ) -> None:
        self.code = code
        self.detail = detail
        self.field = field
        self.unlock = unlock
        super().__init__(f"{code}: {detail} (field={field}; unlock={unlock})")
