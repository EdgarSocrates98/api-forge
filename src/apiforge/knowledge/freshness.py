"""Deterministic freshness checks over local pack metadata and receipts."""

from __future__ import annotations

from datetime import UTC, datetime

from apiforge.contracts.knowledge import (
    FreshnessResult,
    FreshnessState,
    PackFreshness,
    SourceObservation,
)
from apiforge.knowledge.loader import Pack


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def verify_pack_freshness(
    pack: Pack,
    observation: SourceObservation | None,
    *,
    now: str,
) -> FreshnessResult:
    """Return freshness without fetching or rewriting external knowledge."""
    metadata: PackFreshness | None = pack.freshness
    if metadata is None:
        return FreshnessResult(
            state="unknown",
            source=pack.domain,
            reason="pack has no declared freshness metadata",
            next_action="declare a freshness window and collect a read-only receipt",
        )
    if observation is None:
        return FreshnessResult(
            state="unresolved",
            source=pack.domain,
            reason="no read-only source observation receipt is available",
            next_action="collect a read-only source observation",
        )
    try:
        observed_at = _parse(observation.observed_at)
        current = _parse(now)
        expires = _parse(metadata.expires_at) if metadata.expires_at else None
    except ValueError as exc:
        return FreshnessResult(
            state="unresolved",
            source=observation.source,
            reason=f"invalid timestamp: {exc}",
            next_action="repair the receipt timestamp",
        )
    age_seconds = max(0, int((current - observed_at).total_seconds()))
    age_days = age_seconds // 86_400
    if current < observed_at:
        return FreshnessResult(
            state="unresolved",
            source=observation.source,
            observed_at=observation.observed_at,
            reason="observation is in the future relative to the supplied clock",
            next_action="rerun with an explicit consistent clock",
        )
    if expires is not None and current > expires:
        return FreshnessResult(
            state="deprecated",
            source=observation.source,
            observed_at=observation.observed_at,
            age_days=age_days,
            reason=f"pack validity expired at {metadata.expires_at}",
            next_action="retire the pack or declare a new validity window",
            evidence=observation.evidence,
        )
    if metadata.source_hash and observation.source_hash != metadata.source_hash:
        return FreshnessResult(
            state="stale",
            source=observation.source,
            observed_at=observation.observed_at,
            age_days=age_days,
            reason="source hash differs from the pack declaration",
            next_action="review the pack against a new read-only receipt",
        )
    if (
        metadata.source_version
        and observation.source_version
        and observation.source_version != metadata.source_version
    ):
        return FreshnessResult(
            state="stale",
            source=observation.source,
            observed_at=observation.observed_at,
            age_days=age_days,
            reason=(
                f"source version {observation.source_version!r} differs from the "
                f"pack declaration {metadata.source_version!r}"
            ),
            next_action="review the pack against a new read-only receipt",
        )
    version_confirmed = bool(
        metadata.source_version and observation.source_version == metadata.source_version
    )
    if metadata.window_days is None:
        state: FreshnessState = "unknown"
        reason = "pack declares no freshness window"
        next_action = "declare a freshness window"
    elif age_days > metadata.window_days:
        state = "stale"
        reason = f"observation age {age_days}d exceeds window {metadata.window_days}d"
        next_action = "collect a new read-only source observation"
    elif version_confirmed and metadata.source_hash:
        state = "verified"
        reason = "source hash, source version and freshness window all confirmed"
        next_action = "continue with evidence review"
    else:
        state = "fresh"
        reason = "observation is within the declared freshness window"
        next_action = "continue with evidence review"
    return FreshnessResult(
        state=state,
        source=observation.source,
        observed_at=observation.observed_at,
        age_days=age_days,
        reason=reason,
        next_action=next_action,
        evidence=observation.evidence,
    )
