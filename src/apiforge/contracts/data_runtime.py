"""Contracts for provider-neutral, read-only data and broker operations."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

DataProvider = Literal[
    "rds",
    "aurora",
    "redis",
    "mongo",
    "documentdb",
    "dynamodb",
    "neptune",
    "kafka",
    "msk",
    "kinesis",
    "sqs",
    "sns",
    "eventbridge",
    "rabbitmq",
    "nats",
    "pulsar",
]


class DataReadRequest(VersionedContract):
    provider: DataProvider
    resource_ref: str
    operation: str
    params: tuple[tuple[str, str], ...] = ()
    credential_reference: str = "host-managed"


class DataReadReceipt(VersionedContract):
    provider: DataProvider
    resource_ref: str
    operation: str
    status: Literal["executed", "blocked", "failed", "inconclusive"]
    network_called: bool = False
    mutation_performed: bool = False
    response_digest: str | None = None
    evidence: tuple[str, ...] = ()
    violations: tuple[str, ...] = ()
    limitations: tuple[str, ...] = Field(default_factory=tuple)
