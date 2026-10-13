"""Compile migration discovery into a closed TaskSpec and DAG."""

from __future__ import annotations

from typing import Literal, cast

from apiforge.contracts.task import Budgets, Recipe, TaskRisk, TaskSize, TaskSpec
from apiforge.core.ids import stable_id
from apiforge.migration.contracts import (
    DiscoveryResult,
    MigrationPlan,
    MigrationReadiness,
    MigrationSpec,
    MigrationTask,
)


def compile_plan(spec: MigrationSpec, discovery: DiscoveryResult) -> MigrationPlan:
    prefix = stable_id("migration", spec.identity())
    compatibility_id = f"{prefix}:compatibility"
    dependencies_id = f"{prefix}:dependencies"
    contracts_id = f"{prefix}:contracts"
    tasks = (
        MigrationTask(
            id=compatibility_id,
            axis="compatibility",
            outcome="classify runtime compatibility",
            evidence_required=("matrix", "findings"),
        ),
        MigrationTask(
            id=dependencies_id,
            axis="dependencies",
            outcome="inspect dependencies and toolchains",
            dependencies=(compatibility_id,),
            evidence_required=("manifests", "toolchain capability"),
        ),
        MigrationTask(
            id=contracts_id,
            axis="contracts",
            outcome="compare API contracts",
            dependencies=(compatibility_id,),
            evidence_required=("contract diff",),
        ),
        MigrationTask(
            id=f"{prefix}:verification",
            axis="verification",
            outcome="independent verification",
            dependencies=(dependencies_id, contracts_id),
            evidence_required=("receipt", "verification"),
        ),
    )
    task = TaskSpec(
        id=prefix,
        outcome=f"migrate {spec.ecosystem} {spec.source_version} to {spec.target_version}",
        size=TaskSize.M,
        writable_paths=(spec.project_root,),
        inputs=(spec.identity(),),
        dependencies=tuple(item.id for item in tasks if item.dependencies),
        preconditions=("runtime matrix resolved", "project root is readable", "sandbox is active"),
        tests=("migration unit tests", "build/test evidence", "independent verification"),
        expected_proofs=("runtime discovery", "compatibility findings", "diff receipt"),
        budgets=Budgets(max_calls=20, max_rounds=3),
        risk=TaskRisk.LOCAL_REVERSIBLE,
        strategy=Recipe.PLAN_EXECUTE_VERIFY,
        rollback="discard the isolated worktree or restore the pre-migration revision",
        acceptance_criteria=("no critical unresolved finding", "verifier accepts evidence"),
        capability_covered="runtime-migration-control-plane",
    )
    from apiforge.migration.matrix import resolve_versions

    matrix = resolve_versions(spec.ecosystem, spec.source_version, spec.target_version)
    missing = tuple(sorted(cap.name for cap in discovery.capabilities if not cap.available))
    blocking = tuple(sorted(f.rule_id for f in discovery.findings if f.blocking))
    status = "blocked" if missing or blocking else "review" if discovery.findings else "ready"
    return MigrationPlan(
        spec_identity=spec.identity(),
        task=task,
        tasks=tasks,
        findings=discovery.findings,
        capabilities=discovery.capabilities,
        readiness=MigrationReadiness(
            status=cast(Literal["ready", "review", "blocked"], status),
            direction=matrix["direction"],
            intermediate_versions=tuple(matrix["intermediate"]),
            missing_capabilities=missing,
            blocking_findings=blocking,
        ),
    )
