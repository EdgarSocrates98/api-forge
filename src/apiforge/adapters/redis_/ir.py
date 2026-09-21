"""Build a DataAccessIR instance from extracted Redis call-site facts."""

from __future__ import annotations

from apiforge.adapters.inventory import CodeInventory
from apiforge.contracts.stubs import DataAccessIR
from apiforge.core.ids import stable_id


def build_data_access_ir(inventory: CodeInventory) -> DataAccessIR:
    """Aggregate facts into the IR — entities are literal keys only."""
    commands: set[str] = set()
    keys: set[str] = set()
    heuristic_files: set[str] = set()
    for fact in inventory.facts:
        if fact.kind == "data.redis.command":
            commands.add(str(fact.measures.get("command", "")))
            literal = fact.measures.get("key_literal")
            if literal:
                keys.add(str(literal))
            pattern = fact.measures.get("key_pattern")
            if pattern:
                keys.add(str(pattern))
            if fact.measures.get("binding") == "name":
                heuristic_files.add(fact.source.path)
    unresolved = tuple(
        sorted({d.code for d in inventory.diagnostics})
    )
    return DataAccessIR(
        id=stable_id(
            "dataaccess", {"root": inventory.root, "framework": "redis"}
        ),
        produced_by="apiforge",
        database="redis",
        provider="redis|valkey",
        entities=tuple(sorted(keys)),
        access_patterns=tuple(sorted(commands)),
        unresolved=unresolved,
        attributes={
            "command_facts": sum(
                1 for f in inventory.facts if f.kind == "data.redis.command"
            ),
            "heuristic_binding_files": tuple(sorted(heuristic_files)),
            "write_facts": sum(
                1 for f in inventory.facts if f.kind == "data.redis.write"
            ),
        },
    )
