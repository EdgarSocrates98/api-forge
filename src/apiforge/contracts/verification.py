"""Closed contracts for independent task verification and holdouts."""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from apiforge.contracts.base import VersionedContract

ProofAxis = Literal["contract", "security", "idempotency", "pagination"]
ProofVerdict = Literal["pass", "fail", "inconclusive"]


class VerificationCheck(VersionedContract):
    check_id: str
    axis: ProofAxis
    verdict: ProofVerdict
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    limitation: str | None = None


class HoldoutRecord(VersionedContract):
    mutation_id: str
    target: str
    expected_axis: ProofAxis
    detected: bool
    evidence: tuple[str, ...] = ()
    limitation: str | None = None


class VerificationRecord(VersionedContract):
    task_id: str
    revision: int
    run_id: str
    verdict: ProofVerdict
    checks: tuple[VerificationCheck, ...] = ()
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    holdout: tuple[HoldoutRecord, ...] = ()
    verified_by: str

    @model_validator(mode="after")
    def pass_requires_holdout(self) -> VerificationRecord:
        if self.verdict == "pass" and (
            not self.holdout or not all(item.detected for item in self.holdout)
        ):
            raise ValueError("pass requires detected holdout records")
        return self
