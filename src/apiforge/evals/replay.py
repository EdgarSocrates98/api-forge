"""Economy replay (§77–78): re-plan stored decisions under the current policy, no providers.

A stored run keeps its routing decision (``routing.json``) and economy plan
(``economy.json``). Replay strips the stored economy, rebuilds the
pre-economy routing plan, applies the current profile policy and compares:
effective profile, trimmed roles and — the invariant — whether any
risk-required role would now be missing. Runs without a decision are
reported ``unresolved``; nothing is guessed.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from apiforge.contracts.economy_evals import ReplayReport, ReplayRun


def _bundles_from_root(root: Path) -> Iterator[tuple[str, dict[str, Any]]]:
    tasks = Path(root) / ".apiforge" / "tasks"
    if not tasks.is_dir():
        return
    for run_dir in sorted(tasks.glob("*/runs/*")):
        if not run_dir.is_dir():
            continue
        bundle: dict[str, Any] = {"task_id": run_dir.parent.parent.name}
        for name, key in (("routing.json", "routing"), ("economy.json", "economy")):
            path = run_dir / name
            if path.is_file():
                bundle[key] = json.loads(path.read_text(encoding="utf-8"))
        yield f"{run_dir.parent.parent.name}/{run_dir.name}", bundle


def _bundles_from_corpus(corpus: Path) -> Iterator[tuple[str, dict[str, Any]]]:
    for path in sorted(Path(corpus).glob("*.json")):
        yield path.stem, json.loads(path.read_text(encoding="utf-8"))


def _load_task(root: Path | None, bundle: Mapping[str, Any]) -> Any:
    from apiforge.contracts.task import TaskSpec

    if bundle.get("task") is not None:
        return TaskSpec.model_validate(bundle["task"])
    if root is not None:
        from apiforge.taskspec import store as task_store

        return task_store.load(root, str(bundle["task_id"]))
    return None


def replay_bundle(
    name: str, bundle: Mapping[str, Any], *, profile: str | None = None, root: Path | None = None
) -> ReplayRun:
    from apiforge.contracts.economy import EconomyPlan
    from apiforge.contracts.routing import RoutingDecision
    from apiforge.runtime.economy import (
        apply_economy,
        build_economy_plan,
        load_economy_config,
        role_kinds,
    )
    from apiforge.runtime.registry import load_capabilities
    from apiforge.runtime.routing import build_routing_plan, load_routing_policy

    if "routing" not in bundle or "economy" not in bundle:
        return ReplayRun(
            run=name,
            profile=profile or "",
            status="unresolved",
            reason="AF-REPLAY-RUN-INCOMPLETE: stored run lacks routing.json or economy.json",
        )
    try:
        decision = RoutingDecision.model_validate(bundle["routing"]).model_copy(
            update={"economy": None}
        )
        stored = EconomyPlan.model_validate(bundle["economy"])
        spec = _load_task(root, bundle)
    except (ValidationError, OSError, ValueError) as exc:
        return ReplayRun(
            run=name,
            profile=profile or "",
            status="unresolved",
            reason=f"AF-REPLAY-RUN-INCOMPLETE: {exc}",
        )
    if spec is None:
        return ReplayRun(
            run=name,
            profile=profile or "",
            status="unresolved",
            reason="AF-REPLAY-RUN-INCOMPLETE: task spec unavailable",
        )
    catalog = load_capabilities()
    kinds = {key: item.kind for key, item in catalog.items()}
    selected = profile or stored.requested
    plan = build_routing_plan(decision, catalog, policy=load_routing_policy())
    economy = build_economy_plan(
        decision, spec, flag=selected, manifest=None, config=load_economy_config()
    )
    kept, economy = apply_economy(plan, economy, decision, kinds)
    removed = tuple(sorted(set(economy.minimum_roles) - role_kinds(kept, kinds)))
    same = (
        economy.effective == stored.effective
        and tuple(economy.trimmed_roles) == tuple(stored.trimmed_roles)
        and not removed
    )
    return ReplayRun(
        run=name,
        profile=selected,
        status="same" if same else "changed",
        removed_required_roles=removed,
        trimmed_before=tuple(stored.trimmed_roles),
        trimmed_after=tuple(economy.trimmed_roles),
        effective_before=stored.effective,
        effective_after=economy.effective,
        reason="" if same else "policy or profile changes the plan",
    )


def replay(
    *, root: Path | None = None, corpus: Path | None = None, profile: str | None = None
) -> ReplayReport:
    source = (
        _bundles_from_corpus(Path(corpus))
        if corpus is not None
        else _bundles_from_root(Path(root or "."))
    )
    runs = tuple(replay_bundle(name, bundle, profile=profile, root=root) for name, bundle in source)
    removed = sum(len(item.removed_required_roles) for item in runs)
    return ReplayReport(
        runs=runs,
        changed=sum(item.status == "changed" for item in runs),
        unresolved=sum(item.status == "unresolved" for item in runs),
        removed_required_roles=removed,
        passed=removed == 0,
    )


__all__ = ["replay", "replay_bundle"]
