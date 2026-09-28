"""Typed refusals for the field-validation harness."""

from __future__ import annotations

from apiforge.contracts.base import ContractError

TASK_UNREGISTERED = "AF-FIELD-TASK-UNREGISTERED"
LATE_REGISTRATION = "AF-FIELD-LATE-REGISTRATION"
ENUM = "AF-FIELD-ENUM"
FLAG_CONTAMINATION = "AF-FIELD-FLAG-CONTAMINATION"
TIME_ORDER = "AF-FIELD-TIME-ORDER"
EXPORT_LEAK = "AF-FIELD-EXPORT-LEAK"
RUN_MISSING = "AF-FIELD-RUN-MISSING"
CORPUS_INVALID = "AF-FIELD-CORPUS-INVALID"


class FieldError(ContractError):
    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        super().__init__(code, detail)
        self.field = field
        self.unlock = unlock


__all__ = [
    "CORPUS_INVALID",
    "ENUM",
    "EXPORT_LEAK",
    "FLAG_CONTAMINATION",
    "LATE_REGISTRATION",
    "RUN_MISSING",
    "TASK_UNREGISTERED",
    "TIME_ORDER",
    "FieldError",
]
