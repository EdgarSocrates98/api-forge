"""Graph contracts: provenance nodes and edges with closed vocabularies."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue, Sha256, freeze_json


class NodeKind(StrEnum):
    WORKSPACE = "workspace"
    REPOSITORY = "repository"
    SERVICE = "service"
    DEPENDENCY = "dependency"
    RUNTIME = "runtime"
    PROJECT = "project"
    CASE = "case"
    ARTIFACT = "artifact"
    CONTRACT = "contract"
    OPERATION = "operation"
    ROUTE = "route"
    HANDLER = "handler"
    SCHEMA = "schema"
    DATABASE = "database"
    TABLE = "table"
    COLLECTION = "collection"
    INDEX = "index"
    PARTITION = "partition"
    AWS_RESOURCE = "aws_resource"
    RULE = "rule"
    FACT = "fact"
    FINDING = "finding"
    TEST = "test"
    TRACE = "trace"
    METRIC = "metric"
    TASK = "task"
    DECISION = "decision"
    AGENT = "agent"
    RELEASE = "release"
    EVIDENCE = "evidence"


class EdgeKind(StrEnum):
    CONTAINS = "contains"
    EXPOSES = "exposes"
    USES = "uses"
    DECLARED_AS = "declared_as"
    IMPLEMENTED_BY = "implemented_by"
    DESCRIBED_BY = "described_by"
    BACKED_BY = "backed_by"
    DERIVED_FROM = "derived_from"
    DEPENDS_ON = "depends_on"
    CALLS = "calls"
    PERSISTS_TO = "persists_to"
    DEPLOYED_AS = "deployed_as"
    OBSERVED_IN = "observed_in"
    VIOLATES = "violates"
    REMEDIATES = "remediates"
    VERIFIED_BY = "verified_by"
    BLOCKED_BY = "blocked_by"
    SUPERSEDES = "supersedes"
    AUTHORIZED_BY = "authorized_by"
    INVALIDATES = "invalidates"
    AFFECTS = "affects"
    COMPATIBLE_WITH = "compatible_with"


class GraphNode(VersionedContract):
    """A provenance node — deterministic id, closed kind, hashed props."""

    id: str
    kind: NodeKind
    props: Mapping[str, JsonValue] = Field(default_factory=dict)
    sha256: Sha256 | None = None

    @field_validator("props", mode="after")
    @classmethod
    def freeze_props(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("node props must be a JSON object")  # noqa: TRY004
        return frozen


class GraphEdge(VersionedContract):
    """A directed provenance edge between two node ids."""

    from_id: str
    to_id: str
    kind: EdgeKind
    props: Mapping[str, JsonValue] = Field(default_factory=dict)

    @field_validator("props", mode="after")
    @classmethod
    def freeze_props(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("edge props must be a JSON object")  # noqa: TRY004
        return frozen


class GraphExport(VersionedContract):
    """A canonical graph snapshot — deterministic bytes for a given build."""

    nodes_sha256: Sha256
    edges_sha256: Sha256
    node_count: int
    edge_count: int
    built_from: tuple[str, ...] = ()
    format: Literal["jsonl", "neptune"] = "jsonl"
