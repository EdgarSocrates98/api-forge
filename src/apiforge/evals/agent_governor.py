"""Deterministic agent-governor evals: §23-§27 primitives vs declared cases."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.agentic_governance import GovernorInputs
from apiforge.contracts.base import ContractError
from apiforge.governance.gain import expected_gain
from apiforge.governance.governor import govern
from apiforge.governance.loop import check_loop, strategy_fingerprint
from apiforge.governance.recovery import decide_recovery
from apiforge.governance.stop import decide_stop


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"agent-governor corpus {corpus} empty or duplicated"
        )
    return cases


def _check(case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("expect") or {}
    if "govern" in case:
        decision = govern(GovernorInputs.model_validate(case["govern"]))
        expected = expect.get("decision") or {}
        for key, wanted in expected.items():
            actual = getattr(decision, key)
            if isinstance(actual, (tuple, frozenset)):
                actual = list(actual)
            if actual != wanted:
                failures.append(f"decision.{key} {actual} != {wanted}")
        for clamp in expect.get("clamped_by") or ():
            if clamp not in decision.clamped_by:
                failures.append(f"missing clamp {clamp}")
    if "gain" in case:
        spec = case["gain"]
        gain = expected_gain(spec["action"], {k: v for k, v in (spec.get("signals") or {}).items()})
        if "level" in expect and gain.level != expect["level"]:
            failures.append(f"gain.level {gain.level} != {expect['level']}")
        if "score" in expect and (gain.score is None or abs(gain.score - expect["score"]) > 1e-3):
            failures.append(f"gain.score {gain.score} != {expect['score']}")
    if "stop" in case:
        spec = case["stop"]
        gain = expected_gain(spec["action"], dict(spec.get("signals") or {}))
        stop = decide_stop(
            gain,
            mandatory_requirement=bool(spec.get("mandatory", False)),
            threshold=float(spec.get("threshold", 0.33)),
        )
        if "stop_decision" in expect and stop.decision != expect["stop_decision"]:
            failures.append(f"stop {stop.decision} != {expect['stop_decision']}")
        if "stop_code" in expect and stop.code != expect["stop_code"]:
            failures.append(f"stop.code {stop.code} != {expect['stop_code']}")
    if "recovery" in case:
        spec = case["recovery"]
        recovery = decide_recovery(spec["failure_class"], int(spec.get("attempt", 0)))
        if "recovery_decision" in expect and recovery.decision != expect["recovery_decision"]:
            failures.append(f"recovery {recovery.decision} != {expect['recovery_decision']}")
        if "recovery_code" in expect and recovery.code != expect["recovery_code"]:
            failures.append(f"recovery.code {recovery.code} != {expect['recovery_code']}")
    if "loop" in case:
        spec = case["loop"]
        history = [
            strategy_fingerprint(item) if not str(item).startswith("strategy:") else str(item)
            for item in spec.get("strategies") or ()
        ]
        detection = check_loop(
            history,
            window=int(spec.get("window", 5)),
            max_repeats=int(spec.get("max_repeats", 2)),
        )
        if "blocked" in expect and detection.blocked != expect["blocked"]:
            failures.append(f"loop.blocked {detection.blocked} != {expect['blocked']}")


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    _check(case, failures)
    return {"id": case["id"], "passed": not failures, "failures": failures}


def run_agent_governor(corpus: Path) -> dict[str, Any]:
    cases = load_cases(corpus)
    results = [_run_case(case) for case in cases]
    failed = [result["id"] for result in results if not result["passed"]]
    return {
        "schema": "apiforge/agent-governor-evals/v1",
        "corpus": str(corpus),
        "cases": results,
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["load_cases", "run_agent_governor"]
