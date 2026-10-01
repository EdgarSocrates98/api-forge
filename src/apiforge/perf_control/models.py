"""Contracts for declarative load plans; execution remains an external gate."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract


class PerformancePlan(VersionedContract):
    subject: str
    endpoints: tuple[str, ...]
    test_kind: Literal["load", "stress", "spike", "soak", "capacity"] = "load"
    target_tps: float = Field(gt=0)
    duration_s: int = Field(default=60, ge=1)
    warmup_s: int = Field(default=10, ge=0)
    max_error_rate: float = Field(default=0.01, ge=0, le=1)
    max_p99_ms: float = Field(default=500, gt=0)
    generator: Literal["k6", "jmeter", "locust"] = "k6"
    execution_allowed: bool = False
    evidence_required: tuple[str, ...] = (
        "achieved_tps",
        "p99_ms",
        "error_rate",
        "generator_dropped_iterations",
        "downstreams_observed",
    )


class PerformanceAssessment(VersionedContract):
    subject: str
    verdict: Literal["PASS", "FAIL", "INCONCLUSIVE"]
    target_tps: float
    achieved_tps: float | None = None
    p99_ms: float | None = None
    error_rate: float | None = None
    failed_conditions: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    external_execution: bool = False
