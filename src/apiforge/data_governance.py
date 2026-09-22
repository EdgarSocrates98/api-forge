"""Offline data-access governance over the database intermediate representation."""

from __future__ import annotations

from apiforge.adapters.inventory import CodeInventory
from apiforge.contracts.stubs import DataAccessIR, DataAccessReadiness, DataPerformanceProfile
from apiforge.core.ids import stable_id

_MUTATIONS = {
    "redis": {"set", "setex", "hset", "sadd", "lpush", "rpush", "del", "expire"},
    "mongo": {"insert", "insert_one", "insert_many", "update", "update_one", "delete", "delete_one"},
    "dynamo": {"putitem", "updateitem", "deleteitem", "batchwriteitem", "put_item", "update_item", "delete_item"},
    "neptune": {"addv", "adde", "drop", "addvertex", "addedge"},
}


def assess_data_access(
    ir: DataAccessIR,
    *,
    credential_configured: bool = False,
    allow_mutation: bool = False,
) -> DataAccessReadiness:
    """Classify access readiness without connecting to a datastore."""

    database = ir.database.lower()
    if database not in _MUTATIONS:
        raise ValueError(f"unsupported database {ir.database!r}")
    observed = tuple(sorted({pattern.strip().lower() for pattern in ir.access_patterns if pattern.strip()}))
    mutation_patterns = tuple(
        pattern for pattern in observed if pattern in _MUTATIONS[database]
    )
    blockers: list[str] = []
    evidence = ["static-ir-only", "network_called:false", "mutation_performed:false"]
    if not credential_configured:
        blockers.append("credential-not-declared")
    if not observed:
        blockers.append("access-patterns-absent")
    if ir.unresolved:
        blockers.append("unresolved-static-findings")
    if mutation_patterns and not allow_mutation:
        blockers.append("external-mutation-requires-approval")
    if not blockers:
        status = "ready"
        evidence.append("credential-declared")
    elif set(blockers) <= {"credential-not-declared", "access-patterns-absent"}:
        status = "review"
    else:
        status = "blocked"
    return DataAccessReadiness(
        id=f"data-readiness-{ir.id}",
        database=database,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        observed_patterns=observed,
        mutation_patterns=mutation_patterns,
        blockers=tuple(blockers),
        evidence=tuple(evidence),
    )


def build_data_performance_profile(
    inventory: CodeInventory,
    *,
    database: str,
) -> DataPerformanceProfile:
    """Summarize only facts observed by a Redis/Dynamo scanner."""

    if database not in {"redis", "dynamo", "mongo", "neptune"}:
        raise ValueError(f"unsupported database {database!r}")
    signals: set[str] = set()
    risks: set[str] = set()
    for fact in inventory.facts:
        for key, value in fact.measures.items():
            if value is True:
                signals.add(str(key))
        if database == "redis" and fact.kind == "data.redis.write" and "ttl_seconds" not in fact.measures:
            risks.add("write-without-declared-ttl")
        if database == "dynamo" and fact.kind == "data.dynamo.operation":
            if fact.measures.get("full_scan") is True:
                risks.add("full-scan")
            if fact.measures.get("query_without_key_condition") is True:
                risks.add("query-without-key-condition")
    latency_class = {
        "redis": "low_latency", "dynamo": "partitioned_scale",
        "mongo": "document", "neptune": "graph",
    }[database]
    return DataPerformanceProfile(
        id=stable_id("data-profile", {"root": inventory.root, "database": database}),
        database=database,  # type: ignore[arg-type]
        latency_class=latency_class,  # type: ignore[arg-type]
        observed_signals=tuple(sorted(signals)),
        risk_findings=tuple(sorted(risks)),
        unresolved=tuple(sorted(d.code for d in inventory.diagnostics)),
    )
