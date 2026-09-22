"""Offline data-access governance over the database intermediate representation."""

from __future__ import annotations

from apiforge.contracts.stubs import DataAccessIR, DataAccessReadiness

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
