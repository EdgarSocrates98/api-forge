"""Verification state and cycle readiness, derived rather than stored.

A receipt counts only while its annotation digest matches the run; a cycle may
decide H1 only when every scenario has enough agreed runs inside the timebox.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from apiforge.contracts.field import (
    SCENARIOS,
    CorpusManifest,
    CoverageGate,
    CycleStatus,
    FieldRun,
    VerificationState,
)
from apiforge.field.identity import sha256_json
from apiforge.field.store import parse_ts

DIGEST_FIELDS: tuple[str, ...] = (
    "task_id",
    "phase",
    "run_ids",
    "executor",
    "task_completed",
    "exit_reason",
    "manual_context_required",
    "human_intervention",
    "false_positives",
    "false_negatives",
)


def annotation_digest(run: FieldRun) -> str:
    dumped = run.model_dump(mode="json")
    return sha256_json({name: dumped[name] for name in DIGEST_FIELDS})


def verification_state(run: FieldRun) -> VerificationState | None:
    receipt = run.verification
    if receipt is None:
        return None
    if receipt.annotation_sha256 != annotation_digest(run):
        return "stale"
    return receipt.verdict


def utc_now() -> datetime:
    return datetime.now(UTC)


def stamp(moment: datetime) -> str:
    return moment.astimezone(UTC).isoformat().replace("+00:00", "Z")


def deadline(manifest: CorpusManifest) -> datetime | None:
    if manifest.cycle_started_at is None:
        return None
    start = parse_ts(manifest.cycle_started_at, field="cycle_started_at")
    return start + timedelta(weeks=manifest.gate.max_weeks)


def cycle_state(
    manifest: CorpusManifest, runs: tuple[FieldRun, ...], now: datetime | None = None
) -> tuple[CycleStatus, CoverageGate]:
    moment = now or utc_now()
    gate = manifest.gate
    baseline = [run for run in runs if run.phase == "baseline"]
    agreed = [run for run in baseline if verification_state(run) == "agree"]
    counts = {name: sum(1 for run in agreed if run.scenario == name) for name in SCENARIOS}
    enough = all(counts[name] >= gate.min_tasks_per_scenario for name in SCENARIOS)
    end = deadline(manifest)
    in_time = end is None or moment <= end
    within = len(baseline) <= gate.max_runs and in_time
    coverage = CoverageGate(
        enough_scenarios=enough,
        runs_total=len(baseline),
        max_runs=gate.max_runs,
        deadline=stamp(end) if end is not None else None,
        within_timebox=within,
    )
    if enough and within:
        return "ready", coverage
    if len(baseline) >= gate.max_runs or not in_time:
        return "expired", coverage
    return "collecting", coverage


__all__ = [
    "DIGEST_FIELDS",
    "annotation_digest",
    "cycle_state",
    "deadline",
    "stamp",
    "utc_now",
    "verification_state",
]
