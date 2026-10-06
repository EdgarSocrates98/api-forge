"""Bounded shadow challengers (§36–38): learn whether the expensive agent pays off.

Sampling is a pure function of the run id, so a replay makes the same
choice. A sampled challenger runs only from calls left after the verification
reserve; its artifact is stored under ``shadow/`` and compared with the
primary, but it never enters the run's artifacts, gaps or status.

Scope note: this is challenger *sampling*, not a decision-plane route. The
canonical route shadow/assisted/active lifecycle lives in
``apiforge.governance.control_plane``; see
``docs/decisions/API_FORGE_CONTROL_PLANE_MIGRATION_MAP.md``.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence

from apiforge.contracts.selective import ShadowDecision

SCALE = 10_000
SHADOW_BUDGET = "AF-ECONOMY-SHADOW-BUDGET"


def sampled(run_id: str, share: float) -> bool:
    bucket = int(hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:8], 16) % SCALE
    return bucket < round(share * SCALE)


def decide(
    run_id: str,
    share: float,
    challengers: Sequence[str],
    calls_available: int,
) -> ShadowDecision:
    if share <= 0:
        return ShadowDecision(share=share, reason="shadow disabled for this profile")
    if not challengers:
        return ShadowDecision(share=share, reason="no challenger planned")
    if not sampled(run_id, share):
        return ShadowDecision(share=share, reason="run not sampled")
    if calls_available < 1:
        return ShadowDecision(
            share=share,
            sampled=True,
            challenger=challengers[0],
            reason=(
                f"{SHADOW_BUDGET}: field=provider_calls; "
                "unlock=no call left after the verification reserve"
            ),
        )
    return ShadowDecision(
        share=share, sampled=True, challenger=challengers[0], reason="sampled within share"
    )


def sample_rate(run_ids: Sequence[str], share: float) -> float:
    if not run_ids:
        return 0.0
    return sum(sampled(item, share) for item in run_ids) / len(run_ids)


__all__ = ["SCALE", "decide", "sample_rate", "sampled"]
