"""Provenance records for graph projection."""

from apiforge.contracts.observability import ObservationSnapshot


def edges(snapshot: ObservationSnapshot) -> tuple[dict[str, str], ...]:
    return tuple(
        {"from": snapshot.snapshot_id, "to": source, "kind": "derived_from"}
        for source in snapshot.provenance
    )
