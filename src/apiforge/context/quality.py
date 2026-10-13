"""Context Quality Engine: measured metrics over capsule refs + recorded uses.

All inputs are observed artifacts — the ``ContextCapsule``/``ContextRef`` rows
and ``ContextUseRecord`` rows derived from the run ledger (or supplied by eval
fixtures). A metric whose required input was never recorded is emitted as
``unresolved`` with a null value; the engine never estimates silently.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Literal

from apiforge.contracts.base import ContractError
from apiforge.contracts.context import ContextRef
from apiforge.contracts.context_quality import (
    CONSUMED_ACTIONS,
    EVIDENCE_KINDS,
    ContextQualityMetric,
    ContextQualityReport,
    ContextUseRecord,
    MetricBasis,
    RoleContextQuality,
    RoleContextTelemetry,
)


def _round(value: float) -> float:
    return round(value, 4)


def _metric(
    name: str,
    value: float | None,
    *,
    basis: MetricBasis = "observed",
    unit: str = "ratio",
    detail: str = "",
) -> ContextQualityMetric:
    return ContextQualityMetric(
        name=name,  # type: ignore[arg-type]
        value=None if basis == "unresolved" else _round(value if value is not None else 0.0),
        unit=unit,
        basis=basis,
        detail=detail,
    )


def _unresolved(name: str, detail: str) -> ContextQualityMetric:
    return ContextQualityMetric(
        name=name,  # type: ignore[arg-type]
        basis="unresolved",
        detail=detail,
    )


@dataclass
class _RoleBucket:
    assigned: set[str] = field(default_factory=set)
    used: set[str] = field(default_factory=set)
    a_bytes: int = 0
    u_bytes: int = 0


@dataclass
class _TelemRow:
    assigned: set[str] = field(default_factory=set)
    expanded: set[str] = field(default_factory=set)
    cited: set[str] = field(default_factory=set)
    bytes: int = 0
    tokens: list[int] = field(default_factory=list)
    dup: int = 0


def used_uris(uses: Iterable[ContextUseRecord]) -> set[str]:
    """Refs whose content actually reached a consumer (expanded/cited/artifact)."""
    return {use.ref_uri for use in uses if use.action in CONSUMED_ACTIONS}


def assigned_uris(uses: Iterable[ContextUseRecord]) -> set[str]:
    return {use.ref_uri for use in uses if use.action == "assigned"}


def evaluate(
    refs: tuple[ContextRef, ...],
    uses: tuple[ContextUseRecord, ...],
    *,
    run_id: str,
    capsule_id: str | None = None,
    required_uris: Iterable[str] = (),
    required_evidence_uris: Iterable[str] | None = None,
    cache_hits: int | None = None,
    cache_lookups: int | None = None,
) -> ContextQualityReport:
    """Compute the full metric catalog; unknown denominators stay unresolved."""
    unresolved: list[str] = []
    total = len(refs)
    by_uri = {ref.uri: ref for ref in refs}
    used = used_uris(uses) & set(by_uri)
    consumed = [use for use in uses if use.action in CONSUMED_ACTIONS and use.ref_uri in by_uri]

    metrics: list[ContextQualityMetric] = []
    if total == 0:
        unresolved.append("no refs in selection; quality metrics are undefined")
    precision = len(used) / total if total else None
    metrics.append(
        _unresolved("context_precision", "empty selection")
        if precision is None
        else _metric("context_precision", precision, detail=f"{len(used)}/{total} refs used")
    )

    required = set(required_uris)
    if not required:
        metrics.append(
            _unresolved("context_recall", "no required refs declared for this selection")
        )
        unresolved.append("context_recall requires a declared required_refs set")
    else:
        covered = required & set(by_uri)
        metrics.append(
            _metric(
                "context_recall",
                len(covered) / len(required),
                detail=f"{len(covered)}/{len(required)} required refs present",
            )
        )

    declared_evidence = (
        set(required_evidence_uris) if required_evidence_uris is not None else required
    )
    # An explicit required-evidence declaration is authoritative even when a
    # URI was not recovered. Absence is the recall failure, not a reason to
    # remove the item from the denominator.
    required_evidence = (
        declared_evidence
        if required_evidence_uris is not None
        else {
            uri for uri in declared_evidence if uri in by_uri and by_uri[uri].kind in EVIDENCE_KINDS
        }
    )
    if not required_evidence:
        metrics.append(
            _unresolved(
                "evidence_recall",
                "no required evidence refs declared; selected-evidence utilization is not recall",
            )
        )
    else:
        ev_used = required_evidence & used
        metrics.append(
            _metric(
                "evidence_recall",
                len(ev_used) / len(required_evidence),
                detail=f"{len(ev_used)}/{len(required_evidence)} required evidence refs used",
            )
        )

    selected_evidence = {uri for uri, ref in by_uri.items() if ref.kind in EVIDENCE_KINDS}
    selected_evidence_used = selected_evidence & used
    metrics.append(
        _unresolved(
            "selected_evidence_utilization",
            "no evidence refs were selected; utilization is not applicable",
        )
        if not selected_evidence
        else _metric(
            "selected_evidence_utilization",
            len(selected_evidence_used) / len(selected_evidence),
            detail=(
                f"{len(selected_evidence_used)}/{len(selected_evidence)} selected evidence refs used"
            ),
        )
    )

    total_bytes = sum(ref.size_bytes for ref in refs)
    used_bytes = sum(by_uri[uri].size_bytes for uri in used)
    if not total_bytes:
        metrics.append(_unresolved("context_density", "selection carries no bytes"))
    else:
        metrics.append(
            _metric(
                "context_density",
                used_bytes / total_bytes,
                detail=f"{used_bytes}/{total_bytes} bytes used",
            )
        )

    seen: set[tuple[str, tuple[int, int] | None]] = set()
    dup_bytes = 0
    for ref in refs:
        key = (ref.source, ref.span)
        if key in seen:
            dup_bytes += ref.size_bytes
        else:
            seen.add(key)
    if not total_bytes:
        metrics.append(_unresolved("duplicate_context_ratio", "selection carries no bytes"))
    else:
        metrics.append(
            _metric(
                "duplicate_context_ratio",
                dup_bytes / total_bytes,
                detail=f"{dup_bytes} bytes shadow an earlier ref from the same span",
            )
        )

    metrics.append(
        _unresolved("irrelevant_context_ratio", "empty selection")
        if precision is None
        else _metric(
            "irrelevant_context_ratio",
            1.0 - precision,
            detail=f"{total - len(used)} refs never consumed",
        )
    )

    parity_known = [ref for ref in refs if ref.parity is not None]
    if not parity_known:
        metrics.append(
            _unresolved("stale_context_ratio", "no ref carries a parity/freshness verdict")
        )
    else:
        stale = [ref for ref in parity_known if ref.parity is False]
        metrics.append(
            _metric(
                "stale_context_ratio",
                len(stale) / len(parity_known),
                detail=f"{len(stale)}/{len(parity_known)} refs are stale",
            )
        )

    expanded_bytes = sum(use.bytes for use in consumed if use.action == "expanded")
    if not total_bytes:
        metrics.append(_unresolved("context_expansion_rate", "selection carries no bytes"))
    else:
        metrics.append(
            _metric(
                "context_expansion_rate",
                expanded_bytes / total_bytes,
                detail=f"{expanded_bytes} expanded bytes over {total_bytes} selected",
            )
        )

    if not used:
        metrics.append(_unresolved("context_reuse_rate", "no ref was consumed"))
    else:
        owners: dict[str, set[str]] = {}
        for use in consumed:
            owners.setdefault(use.ref_uri, set()).add(use.role or "_")
        multi = sum(1 for uri in used if len(owners.get(uri, ())) > 1)
        metrics.append(
            _metric(
                "context_reuse_rate",
                multi / len(used),
                detail=f"{multi}/{len(used)} used refs served more than one role",
            )
        )

    if cache_hits is None or cache_lookups is None or cache_lookups == 0:
        metrics.append(
            _unresolved("cache_hit_rate", "selection-cache hit/lookup counters not recorded")
        )
    else:
        metrics.append(
            _metric(
                "cache_hit_rate",
                min(cache_hits / cache_lookups, 1.0),
                detail=f"{cache_hits}/{cache_lookups} selection lookups hit cache",
            )
        )

    roles: dict[str, _RoleBucket] = {}
    assigned = [use for use in uses if use.action == "assigned"]
    for use in assigned + consumed:
        bucket = roles.setdefault(use.role or "_", _RoleBucket())
        if use.action == "assigned":
            bucket.assigned.add(use.ref_uri)
            assigned_ref = by_uri.get(use.ref_uri)
            bucket.a_bytes += assigned_ref.size_bytes if assigned_ref is not None else use.bytes
        if use.action in CONSUMED_ACTIONS:
            bucket.used.add(use.ref_uri)
            bucket.u_bytes += use.bytes
    role_rows: list[RoleContextQuality] = []
    eff_values: list[float] = []
    for role in sorted(roles):
        bucket = roles[role]
        n_assigned = len(bucket.assigned)
        n_used = len(bucket.used)
        eff = n_used / n_assigned if n_assigned else (1.0 if n_used else None)
        if eff is not None:
            eff_values.append(eff)
        role_rows.append(
            RoleContextQuality(
                role=role,
                refs_assigned=n_assigned,
                refs_used=n_used,
                bytes_assigned=bucket.a_bytes,
                bytes_used=bucket.u_bytes,
                efficiency=None if eff is None else _round(eff),
            )
        )
    if not eff_values:
        metrics.append(_unresolved("role_context_efficiency", "no per-role use rows recorded"))
    else:
        metrics.append(
            _metric(
                "role_context_efficiency",
                sum(eff_values) / len(eff_values),
                detail=f"{len(eff_values)} roles measured",
            )
        )

    tokens = [use.tokens for use in consumed if use.tokens is not None]
    token_total = sum(tokens) if tokens else None
    if token_total is None or token_total == 0:
        metrics.append(_unresolved("evidence_per_token", "no observed token usage on use records"))
    elif not required_evidence:
        metrics.append(
            _unresolved(
                "evidence_per_token",
                "required evidence refs are undeclared; utilization is not recall",
            )
        )
    else:
        ev_used_n = len(required_evidence & used)
        metrics.append(
            _metric(
                "evidence_per_token",
                ev_used_n / token_total,
                unit="evidence/token",
                detail=f"{ev_used_n} evidence refs over {token_total} tokens",
            )
        )
    metrics.append(
        _unresolved(
            "useful_facts_per_1k_tokens",
            "fact IDs are not recorded; used refs cannot be called facts",
        )
    )

    basis_unresolved = [m.name for m in metrics if m.basis == "unresolved"]
    status: Literal["ready", "degraded", "unresolved"] = (
        "ready"
        if not basis_unresolved
        else ("unresolved" if len(basis_unresolved) == len(metrics) else "degraded")
    )
    return ContextQualityReport(
        run_id=run_id,
        capsule_id=capsule_id,
        refs_total=total,
        refs_used=len(used),
        uses_total=len(uses),
        metrics=tuple(metrics),
        roles=tuple(role_rows),
        unresolved=tuple(
            sorted(
                set(
                    unresolved
                    + [f"{m.name}:{m.detail}" for m in metrics if m.basis == "unresolved"]
                )
            )
        ),
        status=status,
    )


def role_telemetry(
    refs: tuple[ContextRef, ...],
    uses: tuple[ContextUseRecord, ...],
    *,
    run_id: str,
) -> tuple[RoleContextTelemetry, ...]:
    """Per-role counters (prompt §7): loaded, expanded, cited, tokens, evidence,
    cache hits, duplicates and the unused-ref estimate."""
    by_uri = {ref.uri: ref for ref in refs}
    rows: dict[str, _TelemRow] = {}
    for use in uses:
        role = use.role or "_"
        row = rows.setdefault(role, _TelemRow())
        if use.action == "assigned":
            row.assigned.add(use.ref_uri)
            ref = by_uri.get(use.ref_uri)
            row.bytes += ref.size_bytes if ref is not None else use.bytes
        elif use.action == "expanded":
            row.expanded.add(use.ref_uri)
        elif use.action in ("cited", "artifact"):
            row.cited.add(use.ref_uri)
        if use.tokens is not None:
            row.tokens.append(use.tokens)
    out: list[RoleContextTelemetry] = []
    for role in sorted(rows):
        row = rows[role]
        cited = row.cited | row.expanded
        evidence = sum(1 for uri in cited if uri in by_uri and by_uri[uri].kind in EVIDENCE_KINDS)
        out.append(
            RoleContextTelemetry(
                run_id=run_id,
                role=role,
                refs_assigned=len(row.assigned),
                refs_expanded=len(row.expanded),
                refs_cited=len(row.cited),
                context_bytes=row.bytes,
                tokens=sum(row.tokens) if row.tokens else None,
                evidence_refs=evidence,
                duplicates=row.dup,
                unused_refs=len(row.assigned - cited),
            )
        )
    return tuple(out)


def uses_from_ledger(root: object, run_id: str) -> tuple[ContextUseRecord, ...]:
    """Derive use records from the measured run ledger.

    ``context capsule`` admissions -> ``loaded``; ``runtime role:<role>`` rows ->
    ``assigned``; ``context expand`` -> ``expanded``. ``cited``/``artifact`` are
    recorded by callers that produce artifacts and are absent otherwise — they
    stay unresolved instead of being inferred.
    """
    from apiforge.economy import run_ledger

    entries, _ = run_ledger.entries(root)  # type: ignore[arg-type]
    records: list[ContextUseRecord] = []
    seq = 0
    for entry in entries:
        if entry.run_id != run_id:
            continue
        verb = entry.verb
        action: str | None = None
        role: str | None = None
        if verb.startswith("runtime role:"):
            action, role = "assigned", verb.removeprefix("runtime role:")
        elif verb == "context expand":
            action = "expanded"
        elif verb.startswith("context"):
            action = "loaded"
        if action is None:
            continue
        for ref in entry.refs:
            seq += 1
            records.append(
                ContextUseRecord(
                    use_id=f"{run_id}:{seq}",
                    run_id=run_id,
                    ref_uri=ref.uri,
                    action=action,  # type: ignore[arg-type]
                    role=role,
                    bytes=ref.size_bytes,
                    tokens=entry.cost.observed_tokens,
                )
            )
    return tuple(records)


def metric_map(metrics: Iterable[ContextQualityMetric]) -> Mapping[str, ContextQualityMetric]:
    return {metric.name: metric for metric in metrics}


def sha256_uri(seed: str) -> str:
    """Deterministic ctx:// uri for eval fixtures; never a content claim."""
    return f"ctx://sha256/{hashlib.sha256(seed.encode('utf-8')).hexdigest()}"


REFUSAL_PREFIX = "AF-CONTEXT-QUALITY"


def refuse(detail: str) -> ContractError:
    return ContractError(REFUSAL_PREFIX, detail)


__all__ = [
    "assigned_uris",
    "evaluate",
    "metric_map",
    "refuse",
    "role_telemetry",
    "sha256_uri",
    "used_uris",
    "uses_from_ledger",
]
