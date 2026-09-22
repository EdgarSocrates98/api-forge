"""Build a DataAccessIR instance from extracted data-access call-site facts."""

from __future__ import annotations

from apiforge.adapters.inventory import CodeInventory
from apiforge.contracts.stubs import DataAccessIR
from apiforge.core.ids import stable_id

_ENTITY_FIELDS = ("entity", "key_literal", "key_pattern")
_PATTERN_FIELDS = ("operation", "command")


def build_data_access_ir(
    inventory: CodeInventory,
    *,
    database: str = "redis",
    provider: str = "redis|valkey",
) -> DataAccessIR:
    """Aggregate facts into the IR — entities are declared literals only."""
    patterns: set[str] = set()
    entities: set[str] = set()
    heuristic_files: set[str] = set()
    for fact in inventory.facts:
        if not fact.kind.startswith("data."):
            continue
        for field in _ENTITY_FIELDS:
            value = fact.measures.get(field)
            if value:
                entities.add(str(value))
        for field in _PATTERN_FIELDS:
            value = fact.measures.get(field)
            if value:
                patterns.add(str(value))
        if fact.measures.get("binding") == "name":
            heuristic_files.add(fact.source.path)
    unresolved = tuple(
        sorted({d.code for d in inventory.diagnostics})
    )
    return DataAccessIR(
        id=stable_id(
            "dataaccess", {"root": inventory.root, "framework": database}
        ),
        produced_by="apiforge",
        database=database,
        provider=provider,
        entities=tuple(sorted(entities)),
        access_patterns=tuple(sorted(patterns)),
        unresolved=unresolved,
        attributes={
            "data_facts": sum(
                1 for f in inventory.facts if f.kind.startswith("data.")
            ),
            "heuristic_binding_files": tuple(sorted(heuristic_files)),
        },
    )
