import asyncio

from apiforge.contracts.agentic import AgentInvocation
from apiforge.runtime.scheduler import run_bounded


def test_scheduler_runs_independent_invocations() -> None:
    items = tuple(AgentInvocation(invocation_id=str(i), run_id="r", agent="a", capability="c", adapter="fake") for i in range(3))

    async def worker(item: AgentInvocation) -> object:
        return item.invocation_id

    result = asyncio.run(run_bounded(items, worker, limit=2, timeout_seconds=1))
    assert [item.response for item in result] == ["0", "1", "2"]
