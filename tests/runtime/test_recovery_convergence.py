"""Final-convergence recovery ownership: the supervisor consumes the
scheduler's ``InvocationResult.recovery`` and never reclassifies an
invocation failure with a second ``decide_recovery`` call.
"""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.runtime import supervisor
from apiforge.runtime.runner import run_runtime
from tests.runtime.test_runtime import make_task


class _SecurityRefusingAdapter:
    name = "failing"

    async def invoke(self, request):
        raise ContractError("AF-RUNTIME-ADAPTER", "security violation forbidden")


def test_supervisor_uses_the_schedulers_recovery_decision(tmp_path, monkeypatch) -> None:
    make_task(tmp_path)
    calls: list[tuple[object, ...]] = []
    real = supervisor.decide_recovery

    def spy(*args, **kwargs):
        calls.append(args)
        return real(*args, **kwargs)

    monkeypatch.setattr(supervisor, "decide_recovery", spy)

    result = run_runtime(tmp_path, "evolve-orders-api", adapter=_SecurityRefusingAdapter())
    context_path = Path(str(result["run_dir"])) / "governance-context.json"
    context = json.loads(context_path.read_text(encoding="utf-8"))

    # Invocation failures carry the scheduler's canonical decision. The old
    # supervisor-side classifier would have mapped this message to
    # tool_failure -> retry; the scheduler maps it to security_refusal ->
    # escalate — the stored value must be the scheduler's.
    assert context["recovery"]["failure_class"] == "security_refusal"
    assert context["recovery"]["decision"] == "escalate"
    assert context["recoveries"]
    assert all(item["failure_class"] == "security_refusal" for item in context["recoveries"])
    # No second decide_recovery() ran inside the supervisor for the same
    # invocation failures — only post-invocation errors ever reach it, and
    # none occurred here.
    assert calls == []


def test_validation_gap_is_classified_once_at_first_observation(tmp_path, monkeypatch) -> None:
    """Payload validation failures never passed through the scheduler, so the
    supervisor is their first classification point — exactly once each."""
    make_task(tmp_path)
    calls = []
    real = supervisor.decide_recovery

    def spy(*args, **kwargs):
        calls.append(args)
        return real(*args, **kwargs)

    monkeypatch.setattr(supervisor, "decide_recovery", spy)

    from apiforge.runtime.adapters import FakeModelAdapter

    adapter = FakeModelAdapter({name: {"invalid": object()} for name in ("api-contract-review",)})
    result = run_runtime(tmp_path, "evolve-orders-api", adapter=adapter)
    context = json.loads(
        (Path(str(result["run_dir"])) / "governance-context.json").read_text(encoding="utf-8")
    )
    # every classification happened exactly once per error, at the first
    # point that observed it — never re-derived downstream
    assert len(calls) == len(context["recoveries"])
    assert context["recoveries"]
