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
from typing import Any, cast

from apiforge.contracts.agentic_governance import LoopAction, LoopDetection
from apiforge.governance.governor import load_governor_policy

_SUPPORTED_ACTIONS = ("stop", "replan", "fallback", "human")


def strategy_fingerprint(strategy: Any) -> str:
    """Canonical fingerprint: identical strategies hash identically."""
    payload = json.dumps(strategy, sort_keys=True, default=str)
    return f"strategy:{hashlib.sha256(payload.encode()).hexdigest()[:16]}"


def check_loop(
    fingerprints: Sequence[str],
    *,
    window: int = 5,
    max_repeats: int = 2,
    blocked_action: LoopAction = "stop",
) -> LoopDetection:
    """Block when the newest fingerprint already repeated in the window."""
    if blocked_action not in _SUPPORTED_ACTIONS:
        raise ValueError(f"unsupported loop action: {blocked_action}")
    if not fingerprints:
        return LoopDetection(
            strategy_fingerprint="strategy:empty",
            repeats=0,
            window=window,
            blocked=False,
            action=blocked_action,
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
            action=blocked_action,
            code="AF-GOV-LOOP-DETECTED",
            reason=f"strategy repeated {repeats} extra time(s) in a window of {window}",
        )
    return LoopDetection(
        strategy_fingerprint=latest,
        repeats=repeats,
        window=window,
        blocked=False,
        action=blocked_action,
        reason=f"{repeats} repeat(s) within allowed window",
    )


def load_loop_policy() -> dict[str, int | str]:
    """Load bounded loop controls from the authoritative governor policy."""
    row = load_governor_policy().get("loop") or {}
    window = int(row.get("window", 5))
    max_repeats = int(row.get("max_repeats", 2))
    blocked_action = str(row.get("blocked_action", "stop"))
    if window < 1 or max_repeats < 1 or blocked_action not in _SUPPORTED_ACTIONS:
        raise ValueError("governor loop policy must declare positive bounds and a supported action")
    return {
        "window": window,
        "max_repeats": max_repeats,
        "blocked_action": cast(LoopAction, blocked_action),
    }


__all__ = ["check_loop", "load_loop_policy", "strategy_fingerprint"]
