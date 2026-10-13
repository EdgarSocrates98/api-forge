"""Contracts for explicit read-only external observations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue, Sha256, freeze_json

ExternalProvider = Literal["github", "http"]
ExternalStatus = Literal["ok", "review", "failed"]


class ExternalReadRequest(VersionedContract):
    """Bounded input for one provider read; it cannot express a mutation."""

    provider: ExternalProvider
    reference: str
    max_age_seconds: Annotated[int, Field(ge=1, le=86_400)] = 300


class ExternalReadReceipt(VersionedContract):
    """Hash and freshness metadata for one external read observation."""

    schema_version: Literal["af-external-read-receipt/1"] = "af-external-read-receipt/1"
    provider: ExternalProvider
    reference: str
    observed_at: str
    fresh_until: str
    response_sha256: Sha256
    read_only: bool = True
    mutation_allowed: bool = False
    limitations: tuple[str, ...] = ()


class ExternalReadResult(VersionedContract):
    """Provider-neutral read result shared by CLI, MCP and host projections."""

    provider: ExternalProvider
    reference: str
    state: Literal["supported", "heuristic", "unresolved", "unsupported"]
    status: ExternalStatus
    payload: JsonValue = Field(default_factory=dict)
    receipt: ExternalReadReceipt | None = None
    gaps: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @classmethod
    def from_payload(
        cls,
        *,
        provider: ExternalProvider,
        reference: str,
        payload: object,
        receipt: ExternalReadReceipt,
        limitations: tuple[str, ...] = (),
    ) -> ExternalReadResult:
        return cls(
            provider=provider,
            reference=reference,
            state="supported",
            status="ok",
            payload=freeze_json(payload),
            receipt=receipt,
            limitations=limitations,
        )


class GitHubPrReceipt(VersionedContract):
    """Receipt emitted by the dedicated CI GitHub mutation host."""

    schema_version: Literal["af-github-pr-receipt/1"] = "af-github-pr-receipt/1"
    operation: Literal["create_or_reuse", "enable_auto_merge"]
    dry_run: bool = False
    repository: str
    head: str
    base: str
    pull_request: Mapping[str, JsonValue] = Field(default_factory=dict)
    observed_at: str | None = None
    read_only: bool = False
    mutation_allowed: bool = True
    limitations: tuple[str, ...] = ()
