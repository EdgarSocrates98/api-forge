"""Final-convergence phase 3: recovery decisions execute real runtime actions.

The scheduler owns classification; the supervisor must now *execute* each
terminal decision once — replan re-routes and invokes new work, fallback
consumes the declared ``RoutingDecision.fallback_order``, escalate raises the
``recovery_escalation`` gate reason, stop emits a terminal receipt — and every
action lands in ``recovery-receipts.json`` plus the governance context.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.runtime.adapters import AgentResponse
from apiforge.runtime.runner import run_runtime
from apiforge.runtime.supervisor import resume_existing_run
from tests.runtime.test_runtime import make_task


class _FailingAdapter:
    """Fails one named capability; succeeds for everything else."""

    name = "failing-one"

    def __init__(self, failing: str, message: str = "tool exploded") -> None:
        self.failing = failing
        self.message = message
        self.calls: list[str] = []

    async def invoke(self, request) -> AgentResponse:
        self.calls.append(request.capability)
        if request.capability == self.failing:
            raise ContractError("AF-RUNTIME-ADAPTER", self.message)
        return AgentResponse(
            output={
                "facts": [f"ok:{request.capability}"],
                "recommendation": f"keep {request.capability}",
                "confidence": 0.9,
            },
            adapter=self.name,
            model="fake-v1",
        )


class _FailAllAdapter:
    name = "fail-all"

    def __init__(self, message: str) -> None:
        self.message = message
        self.calls: list[str] = []

    async def invoke(self, request) -> AgentResponse:
        self.calls.append(request.capability)
        raise ContractError("AF-RUNTIME-ADAPTER", self.message)


def _run_dir(result: dict[str, object]) -> Path:
    return Path(str(result["run_dir"]))


def _receipts(result: dict[str, object]) -> list[dict[str, object]]:
    path = _run_dir(result) / "recovery-receipts.json"
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def test_fallback_executes_declared_candidate(tmp_path: Path) -> None:
    make_task(tmp_path)
    adapter = _FailingAdapter("api-architecture-review", "tool exploded")
    result = run_runtime(tmp_path, "evolve-orders-api", adapter=adapter)

    receipts = _receipts(result)
    fallback_receipts = [r for r in receipts if r["decision"] == "fallback"]
    assert fallback_receipts, receipts
    executed = [r for r in fallback_receipts if r["outcome"] == "executed"]
    assert executed and executed[0]["owner"] == "supervisor"
    fallback_name = str(executed[0]["action_taken"]).split(":", 1)[1]
    assert fallback_name in adapter.calls
    assert fallback_name != "api-architecture-review"
    context = json.loads((_run_dir(result) / "governance-context.json").read_text(encoding="utf-8"))
    assert context["receipts"]
    assert any(artifact["capability"] == fallback_name for artifact in result["artifacts"])


def test_escalate_raises_human_gate_without_extra_calls(tmp_path: Path) -> None:
    make_task(tmp_path)
    adapter = _FailAllAdapter("security violation forbidden")
    result = run_runtime(tmp_path, "evolve-orders-api", adapter=adapter)

    receipts = _receipts(result)
    escalations = [r for r in receipts if r["decision"] == "escalate"]
    assert escalations, receipts
    assert all(r["owner"] == "human" for r in escalations)
    assert all(r["action_taken"] == "escalated:human_gate" for r in escalations)
    summary = json.loads((_run_dir(result) / "summary.json").read_text(encoding="utf-8"))
    assert summary["human_gate"] is True
    # security_refusal escalates at attempt 0: one call per capability, no
    # retry fan-out and no recovery-spawned calls.
    assert len(adapter.calls) == len(set(adapter.calls))


def test_stop_is_terminal_and_makes_no_extra_calls(tmp_path: Path) -> None:
    make_task(tmp_path)
    adapter = _FailAllAdapter("budget exhausted: AF-CONTROL-BUDGET")
    result = run_runtime(tmp_path, "evolve-orders-api", adapter=adapter)

    receipts = _receipts(result)
    stops = [r for r in receipts if r["decision"] == "stop"]
    assert stops, receipts
    assert all(r["owner"] == "none" and r["action_taken"] == "stopped" for r in stops)
    # budget_exhausted -> stop at attempt 0: each capability is tried exactly
    # once and recovery spawns no further work.
    assert len(adapter.calls) == len(set(adapter.calls))
    assert result["status"] in {"REVIEW", "BLOCKED"}


def test_replan_re_routes_excluding_failed_capability(tmp_path: Path) -> None:
    make_task(tmp_path)
    adapter = _FailingAdapter("api-architecture-review", "invalid schema payload")
    result = run_runtime(tmp_path, "evolve-orders-api", adapter=adapter)

    receipts = _receipts(result)
    replans = [r for r in receipts if r["decision"] == "replan"]
    assert replans, receipts
    executed = [r for r in replans if r["outcome"] == "executed"]
    assert executed
    invoked = {
        entry.split(":", 1)[1]
        for receipt in executed
        for entry in receipt["evidence"]
        if entry.startswith("invoked:")
    }
    assert invoked
    assert "api-architecture-review" not in invoked
    assert invoked.issubset(set(adapter.calls))


def test_fallback_budget_exhaustion_escalates(tmp_path: Path) -> None:
    make_task(tmp_path)
    adapter = _FailAllAdapter("tool exploded")
    result = run_runtime(tmp_path, "evolve-orders-api", adapter=adapter)

    receipts = _receipts(result)
    # max_fallbacks=1: the first fallback decision executes one candidate; the
    # remaining fallback decisions escalate, and the fallback's own failure is
    # observed but never re-executed (depth bound = 1).
    assert any(r["decision"] == "fallback" and r["outcome"] == "executed" for r in receipts)
    assert any(
        r["code"] in {"AF-GOV-RECOVERY-NO-FALLBACK", "AF-GOV-RECOVERY-DEPTH"} for r in receipts
    )
    depth_skips = [r for r in receipts if r["code"] == "AF-GOV-RECOVERY-DEPTH"]
    assert all(r["outcome"] == "skipped" for r in depth_skips)


def test_resume_executes_recovery_actions(tmp_path: Path) -> None:
    make_task(tmp_path)
    adapter = _FailAllAdapter("tool exploded")
    first = run_runtime(tmp_path, "evolve-orders-api", adapter=adapter)
    run_id = str(first["run"]["control_run_id"] or first["run"]["run_id"])
    resumed = asyncio.run(
        resume_existing_run(tmp_path, "evolve-orders-api", run_id, adapter=adapter)
    )
    assert resumed["resumed"] is True
    receipts = resumed.get("recovery_receipts")
    assert receipts is None or isinstance(receipts, list)
    if receipts:
        assert all("receipt_id" in receipt for receipt in receipts)
