"""§27 Loop Detection: strategy fingerprints catch repeated-strategy cycles.

A strategy's fingerprint is the sha256 prefix of its canonical JSON shape —
same plan steps, tools and targets produce the same fingerprint regardless
of prose. ``check_loop`` looks at the trailing ``window`` fingerprints and
blocks when the latest one already repeats ``max_repeats`` times inside it.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from typing import Any

from apiforge.contracts.agentic_governance import LoopDetection


def strategy_fingerprint(strategy: Any) -> str:
    """Canonical fingerprint: identical strategies hash identically."""
    payload = json.dumps(strategy, sort_keys=True, default=str)
    return f"strategy:{hashlib.sha256(payload.encode()).hexdigest()[:16]}"


def check_loop(
    fingerprints: Sequence[str],
    *,
    window: int = 5,
    max_repeats: int = 2,
) -> LoopDetection:
    """Block when the newest fingerprint already repeated in the window."""
    if not fingerprints:
        return LoopDetection(
            strategy_fingerprint="strategy:empty",
            repeats=0,
            window=window,
            blocked=False,
            reason="no strategy recorded yet",
        )
    tail = list(fingerprints)[-window:]
    latest = tail[-1]
    repeats = tail.count(latest) - 1
    if repeats >= max_repeats:
        return LoopDetection(
            strategy_fingerprint=latest,
            repeats=repeats,
            window=window,
            blocked=True,
            code="AF-GOV-LOOP-DETECTED",
            reason=f"strategy repeated {repeats} extra time(s) in a window of {window}",
        )
    return LoopDetection(
        strategy_fingerprint=latest,
        repeats=repeats,
        window=window,
        blocked=False,
        reason=f"{repeats} repeat(s) within allowed window",
    )


__all__ = ["check_loop", "strategy_fingerprint"]
