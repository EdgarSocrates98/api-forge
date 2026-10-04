"""Canonical context and impact application facade."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apiforge.context.service import ContextService
from apiforge.contracts.base import ContractError


def resolve_context(
    root: Path | None = None,
    *,
    scope: str = "repo",
    target: str | None = None,
    impact: str | None = None,
) -> object:
    return ContextService(root).resolve(scope=scope, target=target, impact=impact)


def build_context_capsule(
    root: Path | None = None,
    *,
    target: str,
    case_dir: Path | None = None,
    budget_bytes: int | None = None,
    level: str | None = None,
    impact: str | None = None,
    action: str = "inspect",
    objective: str = "",
    run_id: str | None = None,
    verb: str = "context capsule",
    cache: bool | None = None,
    cache_home: Path | None = None,
) -> dict[str, Any]:
    from apiforge.context.gateway.capsule import (
        DEFAULT_BUDGET_BYTES,
        DEFAULT_IMPACT,
        DEFAULT_LEVEL,
        build_capsule,
        emit,
    )

    selected_level = level or DEFAULT_LEVEL
    if selected_level not in {"L0", "L1", "L2", "L3", "L4"}:
        raise ContractError("AF-CONTEXT-SCOPE-INVALID", f"level {selected_level!r} is not L0-L4")
    selected_impact = impact or DEFAULT_IMPACT
    if selected_impact not in {"direct", "transitive", "all"}:
        raise ContractError(
            "AF-CONTEXT-SCOPE-INVALID", f"impact {selected_impact!r} is not direct|transitive|all"
        )
    capsule = build_capsule(
        Path(root or Path.cwd()),
        target,
        case_dir=case_dir,
        budget_bytes=budget_bytes or DEFAULT_BUDGET_BYTES,
        max_level=selected_level,  # type: ignore[arg-type]
        impact=selected_impact,
        action=action,
        objective=objective,
        run_id=run_id,
        verb=verb,
        cache=cache,
        cache_home=cache_home,
    )
    return emit(capsule)


def expand_context_ref(
    root: Path | None = None, *, uri: str, run_id: str | None = None
) -> dict[str, Any]:
    from apiforge.context.gateway.capsule import expand_ref

    return expand_ref(Path(root or Path.cwd()), uri, run_id=run_id)


def context_quality_report(
    root: Path | None = None,
    *,
    capsule_path: Path,
    run_id: str,
    required_uris: tuple[str, ...] = (),
    gate: str = "strict",
    cache_hits: int | None = None,
    cache_lookups: int | None = None,
) -> dict[str, Any]:
    """Quality report + sufficiency decision for a recorded capsule and run ledger."""
    import json

    from apiforge.context.quality import evaluate, role_telemetry, uses_from_ledger
    from apiforge.context.sufficiency import minimum_sufficient
    from apiforge.contracts.context import ContextCapsule

    if gate not in ("strict", "evidence", "permissive"):
        raise ContractError(
            "AF-CONTEXT-QUALITY-GATE", f"gate {gate!r} is not strict|evidence|permissive"
        )
    try:
        payload = json.loads(Path(capsule_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(
            "AF-CONTEXT-QUALITY-CAPSULE",
            f"cannot read capsule {capsule_path}: {exc}; "
            "unlock=record it with `context capsule ... > capsule.json`",
        ) from exc
    try:
        capsule = ContextCapsule.model_validate(payload)
    except ValueError as exc:
        raise ContractError(
            "AF-CONTEXT-QUALITY-CAPSULE", f"capsule {capsule_path} is not ContextCapsule/v1: {exc}"
        ) from exc
    uses = uses_from_ledger(Path(root or Path.cwd()), run_id)
    report = evaluate(
        capsule.refs,
        uses,
        run_id=run_id,
        capsule_id=capsule.capsule_id,
        required_uris=required_uris,
        cache_hits=cache_hits,
        cache_lookups=cache_lookups,
    )
    sufficiency = minimum_sufficient(
        capsule.refs,
        uses,
        run_id=run_id,
        capsule_id=capsule.capsule_id,
        required_uris=required_uris,
        gate=gate,  # type: ignore[arg-type]
    )
    return {
        "schema": "apiforge/context-quality-run/v1",
        "report": report.model_dump(mode="json"),
        "sufficiency": sufficiency.model_dump(mode="json"),
        "role_telemetry": [
            row.model_dump(mode="json") for row in role_telemetry(capsule.refs, uses, run_id=run_id)
        ],
        "unresolved": list(report.unresolved) + list(sufficiency.unresolved),
    }


__all__ = [
    "build_context_capsule",
    "context_quality_report",
    "expand_context_ref",
    "resolve_context",
]
