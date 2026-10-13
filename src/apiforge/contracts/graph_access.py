"""GraphAccessIR / GraphPlanIR v1 — typed graph-database evidence.

Call sites come from static extraction (no query runs); plans come from
dumps the operator imported or from the allowlisted explain collector.
Anything not observed stays ``unresolved`` — cardinality is never inferred.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

Vendor = Literal["neptune", "neo4j"]
Language = Literal["gremlin", "opencypher", "sparql"]
ShapeRisk = Literal[
    "repeat-without-stop",
    "fanout-without-edge-label",
    "unfiltered-start",
    "open-variable-length-path",
    "unlabeled-node-pattern",
    "cartesian-pattern",
    "unbounded-property-path",
    "dynamic-query-text",
    "analytics-unscoped-algorithm",
    "vector-search-without-topk",
]
PlanFormat = Literal[
    "neptune-gremlin-explain",
    "neptune-gremlin-profile",
    "neptune-opencypher-static",
    "neptune-opencypher-dynamic",
    "neptune-sparql-explain",
    "neo4j-explain",
    "neo4j-profile",
]


class GraphCallSite(VersionedContract):
    """One query or traversal observed in source code."""

    fact_id: str
    vendor: Vendor
    language: Language
    operation: str
    path: str
    line: int
    sha256: str
    query_text: str | None = None
    query_dynamic: bool = False
    bounded: bool
    mutation: bool
    labels_used: tuple[str, ...] = ()
    edge_labels_used: tuple[str, ...] = ()
    shape_risks: tuple[ShapeRisk, ...] = ()


class DomainGraphSketch(VersionedContract):
    """Labels and edges the code names — a draft domain schema, never inferred."""

    vertex_labels: tuple[str, ...] = ()
    edge_labels: tuple[str, ...] = ()
    edges: tuple[tuple[str | None, str, str | None], ...] = ()
    evidence: tuple[str, ...] = ()


class GraphAccessIR(VersionedContract):
    """Aggregate of graph call sites for one project root."""

    id: str
    root: str
    vendors: tuple[Vendor, ...] = ()
    call_sites: tuple[GraphCallSite, ...] = ()
    sketch: DomainGraphSketch = Field(default_factory=DomainGraphSketch)
    unresolved: tuple[str, ...] = ()


class PlanOperator(VersionedContract):
    """One operator or step row of an explain/profile plan."""

    op_id: str
    name: str
    arguments: str = ""
    units_in: int | None = None
    units_out: int | None = None
    estimate: str | None = None
    native: bool = True


class GraphPlanIR(VersionedContract):
    """A parsed plan dump; ``executed`` records whether producing it ran the query."""

    id: str
    format: PlanFormat
    executed: bool
    source_sha256: str
    synthetic: bool = False
    operators: tuple[PlanOperator, ...] = ()
    warnings: tuple[str, ...] = ()
    predicate_count: int | None = None
