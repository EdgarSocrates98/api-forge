"""Progressive external verification (§99): static → test → stop, runtime only when inconclusive.

The table is code on purpose — six fixed, safety-relevant transitions. The
ladder never goes past ``live_read_only``; an inconclusive runtime answer is
``unresolved``, never a mutation.
"""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_resume import VerificationEscalation
from apiforge.contracts.tool_host import TestSlice

_STATIC = ("missing", "likely", "clear", "inconclusive")
_TEST = ("missing", "passed", "failed", "inconclusive")
_RUNTIME = ("missing", "confirmed", "clear", "inconclusive")


def _refusal(code: str, detail: str, field: str, unlock: str) -> ContractError:
    error = ContractError(code, detail)
    error.field = field  # type: ignore[attr-defined]
    error.unlock = unlock  # type: ignore[attr-defined]
    return error


def verdict_from_slice(model: TestSlice) -> tuple[str, tuple[str, ...]]:
    """failed/errors → failed; passed only → passed; nothing ran or gaps → inconclusive."""
    evidence = tuple(f"{item.outcome}: {item.test}" for item in model.failures[:10])
    if model.failed or model.errors:
        return "failed", evidence
    if model.unresolved or model.passed == 0:
        return "inconclusive", (*evidence, *model.unresolved)
    return "passed", (f"{model.passed} passed; log {model.log_ref}",)


def load_slice(path: Path) -> TestSlice:
    try:
        return TestSlice.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        raise _refusal(
            "AF-VERIFY-ESCALATE-INPUT",
            f"{path} is not a TestSlice/v1 JSON: {exc}",
            "test_slice",
            "produce it with `apiforge slice tests <log> > slice.json`",
        ) from exc


def escalate(
    *,
    static: str = "missing",
    test: str | None = None,
    runtime: str = "missing",
    test_slice: Path | None = None,
) -> VerificationEscalation:
    """Return the next verification step; never executes it."""
    evidence: tuple[str, ...] = ()
    if test_slice is not None:
        if test is not None:
            raise _refusal(
                "AF-VERIFY-ESCALATE-INPUT",
                "pass --test or --test-slice, not both",
                "test",
                "drop one of the two",
            )
        test, evidence = verdict_from_slice(load_slice(test_slice))
    test = test or "missing"
    for name, value, allowed in (
        ("static", static, _STATIC),
        ("test", test, _TEST),
        ("runtime", runtime, _RUNTIME),
    ):
        if value not in allowed:
            raise _refusal(
                "AF-VERIFY-ESCALATE-INPUT",
                f"{name} verdict {value!r} is not one of {', '.join(allowed)}",
                name,
                f"use {'|'.join(allowed)}",
            )
    unresolved: tuple[str, ...] = ()
    next_mode: str | None = None
    if test == "failed":
        action, reason = "stop", "test confirms the problem; runtime evidence adds nothing"
    elif test == "passed":
        action, reason = "stop", "test verifies the change; observability is not consulted"
    elif test == "missing":
        action, next_mode = "run_tests", "test"
        reason = (
            "static analysis says a problem is likely; a test must confirm it"
            if static == "likely"
            else "no test verdict yet; tests run before any runtime evidence"
        )
    elif runtime == "missing":
        action, next_mode = "escalate", "live_read_only"
        reason = "test inconclusive; read-only runtime evidence is the next step"
    elif runtime in {"confirmed", "clear"}:
        action = "stop"
        reason = f"read-only runtime evidence is {runtime}; no further escalation"
    else:
        action = "unresolved"
        reason = "test and read-only runtime evidence are both inconclusive"
        unresolved = (
            (
                "AF-VERIFY-ESCALATE-EXHAUSTED: read-only evidence exhausted; mutation is never "
                "the next step; unlock=add a targeted test or a human review"
            ),
        )
    return VerificationEscalation(
        static=static,  # type: ignore[arg-type]
        test=test,  # type: ignore[arg-type]
        runtime=runtime,  # type: ignore[arg-type]
        action=action,  # type: ignore[arg-type]
        next_mode=next_mode,  # type: ignore[arg-type]
        reason=reason,
        test_evidence=evidence,
        unresolved=unresolved,
    )


__all__ = ["escalate", "load_slice", "verdict_from_slice"]
