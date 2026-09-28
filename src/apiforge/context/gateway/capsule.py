"""Build ContextCapsule/v1 under a byte budget and expand ctx:// refs on demand."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from apiforge.cache.store import CacheStore
from apiforge.context.gateway import selection_cache
from apiforge.context.gateway.canonical import digest, dumps, uri_for
from apiforge.context.gateway.levels import (
    Candidate,
    Selection,
    fingerprint,
    load_graph,
    parse_target,
    route_facts_for,
    safe_input,
    select,
    verified_case,
)
from apiforge.context.gateway.refs import CtxStore
from apiforge.contracts.cache import CacheDecision
from apiforge.contracts.context import (
    CapsuleBudget,
    CapsuleLevel,
    CapsuleRefusal,
    ContextCapsule,
    ContextRef,
    ContextScope,
)
from apiforge.contracts.economy import CostVector, LedgerRef, LedgerSource, RunLedgerEntry
from apiforge.economy import run_ledger

DEFAULT_BUDGET_BYTES = 16000
DEFAULT_LEVEL: CapsuleLevel = "L3"
DEFAULT_IMPACT = "transitive"
LEVELS: tuple[CapsuleLevel, ...] = ("L0", "L1", "L2", "L3", "L4")
_REFUSAL_RESERVE = 320


def emit(capsule: ContextCapsule) -> dict[str, Any]:
    """Transport projection: defaults dropped, identity fields always kept."""
    payload = capsule.model_dump(mode="json", exclude_defaults=True)
    payload["schema"] = capsule.schema
    payload["version"] = capsule.version
    payload.setdefault("status", capsule.status)
    return payload


def build_capsule(
    root: Path,
    target: str,
    *,
    case_dir: Path | None = None,
    budget_bytes: int = DEFAULT_BUDGET_BYTES,
    max_level: CapsuleLevel = DEFAULT_LEVEL,
    impact: str = DEFAULT_IMPACT,
    action: str = "inspect",
    objective: str = "",
    run_id: str | None = None,
    verb: str = "context capsule",
    cache: bool | None = None,
    cache_home: Path | None = None,
    on_decision: Callable[[CacheDecision], None] | None = None,
) -> ContextCapsule:
    started = time.perf_counter()
    root = Path(root).resolve()
    case_path = Path(case_dir).resolve() if case_dir else root / ".apiforge" / "case"
    method, path = parse_target(target)
    target = f"{method} {path}"
    intent = {"action": action, "target": target, **({"objective": objective} if objective else {})}
    scope = ContextScope(scope="target", root=".", target=target, impact=impact)
    budget = CapsuleBudget(context_bytes=budget_bytes, max_level=max_level)
    case = verified_case(case_path)
    if case is None:
        capsule = _degraded(root, intent, scope, budget, case_path)
        return _finish(root, capsule, [], verb, run_id, started)
    selection, decision = _selected(
        root, case_path, case, target, impact, CacheStore(root, home=cache_home, enabled=cache)
    )
    if on_decision is not None and decision is not None:
        on_decision(decision)
    selection_hits = int(decision is not None and decision.action in {"reuse", "reuse_warn"})
    store = CtxStore(root)
    base = ContextCapsule(
        capsule_id=uri_for(""),
        run_id="pending",
        intent=intent,
        scope=scope,
        fingerprint=selection.fingerprint,
        impact=selection.impact,
        policies=selection.policies,
        budget=budget.model_copy(update={"reached_level": "L2"}),
        unresolved=tuple(selection.unresolved),
    )
    refs, hits, exhausted = _admit(store, selection, base, budget_bytes, max_level)
    reached: CapsuleLevel = "L2" if exhausted else ("L4" if max_level == "L4" else "L3")
    if max_level in {"L0", "L1", "L2"}:
        reached = max_level
    refusals: tuple[CapsuleRefusal, ...] = ()
    if exhausted:
        refusals = (
            CapsuleRefusal(
                code="AF-CONTEXT-BUDGET-EXHAUSTED",
                field="budget_bytes",
                unlock="raise --budget-bytes or lower --level, then rebuild",
                detail=f"{len(selection.candidates) - len(refs)} evidence refs did not fit {budget_bytes} bytes",
            ),
        )
    capsule = base.model_copy(
        update={
            "refs": tuple(refs),
            "budget": budget.model_copy(update={"reached_level": reached}),
            "refusals": refusals,
            "status": "unresolved" if exhausted else "ready",
        }
    )
    return _finish(root, capsule, refs, verb, run_id, started, cache_hits=hits + selection_hits)


def _selected(
    root: Path,
    case_path: Path,
    case: dict[str, Any],
    target: str,
    impact: str,
    store: CacheStore,
) -> tuple[Selection, CacheDecision | None]:
    """L4: reuse a fresh cached selection, else select and record its dependencies."""
    if not store.enabled:
        return select(root, case_path, case, target, impact), None
    inputs = case.get("inputs") or {}
    refused: list[str] = []
    contract_rel = _rel(safe_input(root, inputs.get("contract", ""), refused), root)
    project = safe_input(root, inputs.get("project", ""), refused)
    key = selection_cache.selection_key(target, impact, contract_rel, _rel(project, root))
    nodes, edges, graph = load_graph(root, case_path)
    probe = selection_cache.RootProbe(root, project, store, nodes, edges)
    decision, payload = store.lookup(selection_cache.LAYER, key, probe=probe)
    if payload is not None:
        restored = selection_cache.restore(payload, fingerprint(case, root))
        if restored is not None:
            return restored, decision
        decision = decision.model_copy(
            update={"state": "corrupt", "action": "recompute", "reason": "unrestorable payload"}
        )
    selection = select(root, case_path, case, target, impact, cache=store)
    method, path = parse_target(target)
    target_id = f"operation:{method} {path}"
    facts = {
        edge.to_id
        for edge in edges
        if edge.from_id == target_id and edge.kind.value == "implemented_by"
    } | set(route_facts_for(case, method, path))
    files, dep_nodes, symbols = selection_cache.dependencies(
        root, selection, target_id, contract_rel, facts
    )
    store.put(
        selection_cache.LAYER,
        key,
        selection_cache.serialize(selection),
        subject=target,
        inputs_sha=graph,
        deps_files=files,
        deps_nodes=dep_nodes,
        neighborhood_sha=selection_cache.neighborhood(nodes, edges, dep_nodes),
        symbols=symbols,
        manifest=selection_cache.manifest_text(root, project),
    )
    return selection, decision


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def expand_ref(root: Path, uri: str, *, run_id: str | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    root = Path(root).resolve()
    content = CtxStore(root).get(uri)
    size = len(content.encode("utf-8"))
    source: LedgerSource = "filesystem"
    label = uri
    if run_id is not None:
        for row in run_ledger.entries(root)[0]:
            if row.run_id == run_id:
                for ref in row.refs:
                    if ref.uri == uri:
                        source, label = row.source, ref.label
    run_ledger.append(
        root,
        RunLedgerEntry(
            run_id=run_id or "adhoc",
            verb="context expand",
            source=source,
            cost=CostVector(tool_result_bytes=size, expansions=1, duration_ms=_ms(started)),
            refs=(LedgerRef(uri=uri, label=label, provenance="expand:on-demand", size_bytes=size),),
        ),
    )
    return {
        "schema": "apiforge/context-expansion/v1",
        "uri": uri,
        "label": label,
        "size_bytes": size,
        "verified": True,
        "content": content,
    }


def _admit(
    store: CtxStore,
    selection: Selection,
    base: ContextCapsule,
    budget_bytes: int,
    max_level: CapsuleLevel,
) -> tuple[list[ContextRef], int, bool]:
    if LEVELS.index(max_level) < LEVELS.index("L3"):
        return [], 0, False
    used = len(dumps(emit(base))) + _REFUSAL_RESERVE
    refs: list[ContextRef] = []
    hits = 0
    for candidate in selection.candidates:
        ref = _ref(candidate, "L3")
        cost = len(dumps(ref.model_dump(mode="json", exclude_defaults=True))) + 1
        if used + cost > budget_bytes:
            return refs, hits, True
        hits += int(store.exists(ref.uri))
        store.put(candidate.content)
        refs.append(ref)
        used += cost
    if max_level == "L4":
        focused: list[ContextRef] = []
        for ref in refs:
            if ref.kind == "code" and ref.parity is None:
                content = store.get(ref.uri)
                extra = len(dumps(content)) + 12
                if used + extra > budget_bytes:
                    return refs, hits, True
                used += extra
                ref = ref.model_copy(update={"excerpt": content, "level": "L4"})
            focused.append(ref)
        refs = focused
    return refs, hits, False


def _ref(candidate: Candidate, level: CapsuleLevel) -> ContextRef:
    return ContextRef(
        uri=uri_for(candidate.content),
        kind=candidate.kind,
        label=candidate.label,
        source=candidate.source,
        span=candidate.span,
        size_bytes=len(candidate.content.encode("utf-8")),
        provenance=candidate.provenance,
        origin=candidate.origin,
        level=level,
        parity=candidate.parity,
        delta=candidate.delta,
    )


def _degraded(
    root: Path,
    intent: dict[str, str],
    scope: ContextScope,
    budget: CapsuleBudget,
    case_path: Path,
) -> ContextCapsule:
    fingerprint: dict[str, object] = {"case": "missing"}
    reached: CapsuleLevel = "L0"
    try:
        from apiforge.context.service import ContextService

        result = ContextService(root).resolve(scope="repo")
        fingerprint = {
            "case": "missing",
            "included_repositories": list(result.included_repositories),
            "targets": len(result.targets),
        }
        reached = "L1"
    except (ValueError, OSError):
        pass
    return ContextCapsule(
        capsule_id=uri_for(""),
        run_id="pending",
        intent=intent,
        scope=scope,
        fingerprint=fingerprint,
        budget=budget.model_copy(update={"reached_level": reached}),
        refusals=(
            CapsuleRefusal(
                code="AF-CTX-GRAPH-UNAVAILABLE",
                field="case_dir",
                unlock=f"run `apiforge analyze --out-dir {case_path}` to build the API graph",
                detail=f"no case.json under {case_path}; capsule stops at {reached}",
            ),
        ),
        unresolved=("graph-unavailable",),
        status="degraded",
    )


def _finish(
    root: Path,
    capsule: ContextCapsule,
    refs: list[ContextRef],
    verb: str,
    run_id: str | None,
    started: float,
    *,
    cache_hits: int = 0,
) -> ContextCapsule:
    body = emit(capsule)
    for key in ("capsule_id", "run_id"):
        body.pop(key, None)
    body["budget"].pop("serialized_bytes", None)
    capsule_id = "ctx://sha256/" + digest(dumps(body).decode("utf-8"))
    capsule = capsule.model_copy(
        update={"capsule_id": capsule_id, "run_id": run_id or f"run-{capsule_id[-16:]}"}
    )
    for _ in range(3):
        size = len(dumps(emit(capsule)))
        if size == capsule.budget.serialized_bytes:
            break
        capsule = capsule.model_copy(
            update={"budget": capsule.budget.model_copy(update={"serialized_bytes": size})}
        )
    _record(root, capsule, refs, verb, started, cache_hits)
    return capsule


def _record(
    root: Path,
    capsule: ContextCapsule,
    refs: list[ContextRef],
    verb: str,
    started: float,
    cache_hits: int,
) -> None:
    grouped: dict[LedgerSource, list[ContextRef]] = {}
    for ref in refs:
        grouped.setdefault(ref.origin, []).append(ref)
    ref_bytes = 0
    duration = _ms(started)
    for source, items in sorted(grouped.items()):
        sizes = [len(dumps(item.model_dump(mode="json", exclude_defaults=True))) for item in items]
        size = sum(sizes)
        ref_bytes += size
        run_ledger.append(
            root,
            RunLedgerEntry(
                run_id=capsule.run_id,
                verb=verb,
                source=source,
                cost=CostVector(context_bytes=size),
                refs=tuple(
                    LedgerRef(
                        uri=item.uri,
                        label=item.label,
                        provenance=item.provenance,
                        size_bytes=item_size,
                    )
                    for item, item_size in zip(items, sizes, strict=True)
                ),
            ),
        )
    run_ledger.append(
        root,
        RunLedgerEntry(
            run_id=capsule.run_id,
            verb=verb,
            source="envelope",
            cost=CostVector(
                context_bytes=max(0, capsule.budget.serialized_bytes - ref_bytes),
                cache_hits=cache_hits,
                duration_ms=duration,
            ),
        ),
    )


def _ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


__all__ = [
    "DEFAULT_BUDGET_BYTES",
    "DEFAULT_IMPACT",
    "DEFAULT_LEVEL",
    "build_capsule",
    "emit",
    "expand_ref",
]
