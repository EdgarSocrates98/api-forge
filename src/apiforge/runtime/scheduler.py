"""Dependency-aware bounded async fan-out."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from apiforge.contracts.agentic import AgentInvocation, InvocationStatus
from apiforge.contracts.base import ContractError


@dataclass(frozen=True, slots=True)
class InvocationResult:
    invocation: AgentInvocation
    response: object | None
    error: str | None = None


async def run_bounded(
    invocations: tuple[AgentInvocation, ...],
    worker: Callable[[AgentInvocation], Awaitable[object]],
    *,
    limit: int,
    timeout_seconds: int,
    max_calls: int | None = None,
    max_retries: int = 0,
    parallelism: Callable[[int, int], int] | None = None,
) -> tuple[InvocationResult, ...]:
    if limit < 1:
        raise ContractError("AF-RUNTIME-BUDGET", "parallel limit must be positive")
    pending = {item.invocation_id: item for item in invocations}
    if max_calls is not None and len(pending) > max_calls:
        raise ContractError("AF-RUNTIME-BUDGET", f"invocations exceed max_calls={max_calls}")
    if max_retries < 0:
        raise ContractError("AF-RUNTIME-BUDGET", "max_retries cannot be negative")
    completed: dict[str, InvocationResult] = {}

    async def execute(item: AgentInvocation, semaphore: asyncio.Semaphore) -> InvocationResult:
        async with semaphore:
            last_failure: InvocationResult | None = None
            for retry_count in range(max_retries + 1):
                running = item.model_copy(
                    update={"status": InvocationStatus.RUNNING, "retry_count": retry_count}
                )
                try:
                    response = await asyncio.wait_for(worker(running), timeout=timeout_seconds)
                except TimeoutError:
                    last_failure = InvocationResult(
                        running.model_copy(
                            update={
                                "status": InvocationStatus.FAILED,
                                "error_code": "AF-RUNTIME-TIMEOUT",
                            }
                        ),
                        None,
                        "AF-RUNTIME-TIMEOUT",
                    )
                except (ContractError, RuntimeError, ValueError, TypeError) as exc:
                    last_failure = InvocationResult(
                        running.model_copy(
                            update={
                                "status": InvocationStatus.FAILED,
                                "error_code": getattr(exc, "code", "AF-RUNTIME-ADAPTER"),
                            }
                        ),
                        None,
                        str(exc),
                    )
                else:
                    return InvocationResult(
                        running.model_copy(update={"status": InvocationStatus.SUCCEEDED}), response
                    )
            if last_failure is None:
                raise ContractError("AF-RUNTIME-ADAPTER", "worker failed without a result")
            return last_failure

    while pending:
        failed_ids = {
            result.invocation.invocation_id
            for result in completed.values()
            if result.invocation.status in {InvocationStatus.FAILED, InvocationStatus.CANCELLED}
        }
        blocked = tuple(
            item
            for item in pending.values()
            if any(dependency in failed_ids for dependency in item.dependencies)
        )
        for item in blocked:
            pending.pop(item.invocation_id, None)
            completed[item.invocation_id] = InvocationResult(
                item.model_copy(
                    update={
                        "status": InvocationStatus.SKIPPED,
                        "error_code": "AF-RUNTIME-DEPENDENCY-FAILED",
                    }
                ),
                None,
                "AF-RUNTIME-DEPENDENCY-FAILED",
            )
        if not pending:
            break
        ready = tuple(
            item
            for item in pending.values()
            if all(dependency in completed for dependency in item.dependencies)
            and not any(dependency in failed_ids for dependency in item.dependencies)
        )
        if not ready:
            unresolved = ", ".join(sorted(pending))
            raise ContractError(
                "AF-RUNTIME-DEPENDENCY", f"dependency cycle or missing dependency: {unresolved}"
            )
        batch_limit = limit
        if parallelism is not None:
            batch_limit = parallelism(len(ready), len(pending))
        if batch_limit < 1 or batch_limit > limit:
            raise ContractError("AF-RUNTIME-BUDGET", "dynamic parallelism must be within 1..limit")
        semaphore = asyncio.Semaphore(batch_limit)
        batch = await asyncio.gather(
            *(execute(item, semaphore) for item in sorted(ready, key=lambda x: x.invocation_id))
        )
        for result in batch:
            pending.pop(result.invocation.invocation_id, None)
            completed[result.invocation.invocation_id] = result
    return tuple(completed[key] for key in sorted(completed))
