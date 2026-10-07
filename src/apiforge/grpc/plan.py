"""Compile gRPC intentions into a bounded, reviewable plan."""

from __future__ import annotations

from typing import Literal

from apiforge.contracts.grpc import GrpcIR, GrpcPlan
from apiforge.contracts.task import Budgets, Recipe, TaskRisk, TaskSize, TaskSpec


def compile_plan(
    intention: str, ir: GrpcIR, risk: Literal["low", "medium", "high", "critical"] = "medium"
) -> GrpcPlan:
    phases: tuple[str, ...] = (
        "discover",
        "analyze",
        "compatibility",
        "capabilities",
        "test",
        "verify",
    )
    if "generate" in intention.lower():
        phases = phases[:4] + ("codegen", "gateway") + phases[4:]
    if "benchmark" in intention.lower() or "performance" in intention.lower():
        phases = phases[:4] + ("benchmark",) + phases[4:]
    return GrpcPlan(
        intention=intention,
        phases=phases,
        risk=risk,
        requires_review=risk in {"high", "critical"},
        proof_axes=("contract", "compatibility", "security", "performance", "evidence"),
        metadata={"source": ir.source_path},
    )


def compile_task_spec(intention: str, ir: GrpcIR, risk: TaskRisk = TaskRisk.READ_ONLY) -> TaskSpec:
    grpc_plan = compile_plan(
        intention,
        ir,
        "high"
        if risk
        in {
            TaskRisk.SENSITIVE,
            TaskRisk.EXTERNAL_MUTATION,
            TaskRisk.DESTRUCTIVE,
            TaskRisk.IRREVERSIBLE,
        }
        else "medium",
    )
    task_id = f"grpc-{ir.source_sha256[:12]}"
    return TaskSpec(
        id=task_id,
        outcome=intention,
        size=TaskSize.M,
        inputs=(ir.source_path,),
        tests=("grpc vertical slice",),
        expected_proofs=grpc_plan.proof_axes,
        budgets=Budgets(max_calls=20, max_rounds=3),
        risk=risk,
        strategy=Recipe.PLAN_EXECUTE_VERIFY,
        rollback="discard local generated artifacts",
        acceptance_criteria=(
            "compatibility verdict is explicit",
            "all unsupported capabilities are named",
            "independent verification completes",
        ),
        capability_covered="grpc-contract-control-plane",
    )
