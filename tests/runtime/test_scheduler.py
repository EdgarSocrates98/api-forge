import asyncio

from apiforge.contracts.agentic import AgentInvocation
from apiforge.contracts.base import ContractError
from apiforge.runtime.scheduler import run_bounded


def test_scheduler_runs_independent_invocations() -> None:
    items = tuple(
        AgentInvocation(invocation_id=str(i), run_id="r", agent="a", capability="c", adapter="fake")
        for i in range(3)
    )

    async def worker(item: AgentInvocation) -> object:
        return item.invocation_id

    result = asyncio.run(run_bounded(items, worker, limit=2, timeout_seconds=1))
    assert [item.response for item in result] == ["0", "1", "2"]


def test_scheduler_rejects_invocations_over_call_budget() -> None:
    items = tuple(
        AgentInvocation(invocation_id=str(i), run_id="r", agent="a", capability="c", adapter="fake")
        for i in range(3)
    )

    async def worker(item: AgentInvocation) -> object:
        return item.invocation_id

    try:
        asyncio.run(run_bounded(items, worker, limit=2, timeout_seconds=1, max_calls=2))
    except ContractError as exc:
        assert "AF-RUNTIME-BUDGET" in str(exc)
    else:
        raise AssertionError("expected call budget refusal")


def test_scheduler_accepts_dynamic_parallelism_within_bound() -> None:
    items = tuple(
        AgentInvocation(invocation_id=str(i), run_id="r", agent="a", capability="c", adapter="fake")
        for i in range(3)
    )

    async def worker(item: AgentInvocation) -> object:
        return item.invocation_id

    result = asyncio.run(
        run_bounded(
            items,
            worker,
            limit=3,
            timeout_seconds=1,
            parallelism=lambda ready, remaining: min(2, ready),
        )
    )
    assert len(result) == 3


def test_scheduler_retries_and_skips_dependents_after_failure() -> None:
    items = (
        AgentInvocation(
            invocation_id="root", run_id="r", agent="a", capability="c", adapter="fake"
        ),
        AgentInvocation(
            invocation_id="child",
            run_id="r",
            agent="a",
            capability="c",
            adapter="fake",
            dependencies=("root",),
        ),
    )
    calls = 0

    async def worker(item: AgentInvocation) -> object:
        nonlocal calls
        calls += 1
        raise RuntimeError("broken")

    result = asyncio.run(run_bounded(items, worker, limit=1, timeout_seconds=1, max_retries=1))
    assert calls == 2
    by_id = {item.invocation.invocation_id: item for item in result}
    assert by_id["root"].invocation.status.value == "failed"
    assert by_id["child"].invocation.status.value == "skipped"
