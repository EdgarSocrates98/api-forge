"""Governed errors for the API/Git/CI change-control application."""

from __future__ import annotations


class ChangeControlError(ValueError):
    """A change-control refusal with a stable AF error code."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")
