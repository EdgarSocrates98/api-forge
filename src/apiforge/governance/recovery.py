"""§26 Recovery Governance: failure classes walk a declared strategy ladder.

Each class in ``rules/recovery_policy.yaml`` declares an ordered strategy
walked by attempt number and a ``max_attempts`` cap. When the cap is
exhausted the ladder's terminal action fires — always ``escalate`` or
``stop``, never a silent extra retry. An undeclared class resolves to
``escalate`` named as such.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

from apiforge.contracts.agentic_governance import (
    FailureClass,
    RecoveryDecision,
)

RECOVERY_POLICY = Path(__file__).resolve().parent.parent / "rules" / "recovery_policy.yaml"


def classify_failure(error_code: str, message: str = "") -> FailureClass:
    """Map an error code/message onto the closed §26 failure-class vocabulary.

    This is the single classification surface: the scheduler calls it at the
    failure site and the supervisor calls it only for post-invocation errors
    (e.g. payload validation gaps) that never carried a scheduler decision.
    """
    text = f"{error_code} {message}".lower()
    if "timeout" in text:
        return "timeout"
    if "security" in text or "unauthor" in text or "forbidden" in text:
        return "security_refusal"
    if "budget" in text or "exhaust" in text:
        return "budget_exhausted"
    if "policy" in text or "refus" in text:
        return "policy_conflict"
    if "schema" in text or "invalid" in text or "contract" in text:
        return "invalid_input"
    if "provider" in text:
        return "provider_failure"
    return "tool_failure"


def load_recovery_policy(path: Path = RECOVERY_POLICY) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "apiforge/recovery-policy/v1":
        raise ValueError(f"{path} is not an apiforge/recovery-policy/v1 file")
    return data


def decide_recovery(
    failure_class: FailureClass | str,
    attempt: int,
    policy: dict[str, Any] | None = None,
) -> RecoveryDecision:
    """Pick the governed recovery action for ``failure_class`` at ``attempt``.

    The failure-class vocabulary is closed (§26): an unknown class refuses
    ``AF-GOV-FAILURE-CLASS-UNKNOWN`` rather than being silently mapped.
    """
    from typing import get_args

    from apiforge.economy.run_ledger import EconomyError

    policy = policy if policy is not None else load_recovery_policy()
    if failure_class not in get_args(FailureClass):
        raise EconomyError(
            "AF-GOV-FAILURE-CLASS-UNKNOWN",
            f"undeclared failure class {failure_class!r}; "
            f"allowed: {sorted(get_args(FailureClass))}",
            field="failure_class",
            unlock="classify the failure into one of the §26 classes",
        )
    klass = cast(FailureClass, failure_class)
    row = (policy.get("classes") or {}).get(str(klass))
    if row is None:
        return RecoveryDecision(
            failure_class=klass,
            decision="escalate",
            attempt=attempt,
            max_attempts=0,
            reason=f"no declared strategy for {klass}; escalating",
            code="AF-GOV-RECOVERY-UNDECLARED",
            unresolved=(str(klass),),
        )
    strategy = list(row.get("strategy") or ["stop"])
    max_attempts = int(row.get("max_attempts", 0))
    if attempt > max_attempts:
        decision = strategy[-1]
        return RecoveryDecision(
            failure_class=klass,
            decision=decision,
            attempt=attempt,
            max_attempts=max_attempts,
            reason=f"attempts exhausted for {klass}; terminal {decision}",
            code="AF-GOV-RECOVERY-EXHAUSTED",
        )
    decision = strategy[min(attempt, len(strategy) - 1)]
    return RecoveryDecision(
        failure_class=klass,
        decision=decision,
        attempt=attempt,
        max_attempts=max_attempts,
        reason=f"{klass} attempt {attempt} -> {decision}",
    )


__all__ = ["RECOVERY_POLICY", "classify_failure", "decide_recovery", "load_recovery_policy"]
