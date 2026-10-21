"""Cross-engine delegation contracts for the forge-doctor-api lane (lf-0030, PHASE 7).

api-forge cannot import ``theforge`` — these models implement the equivalent
semantics of ``theforge/SpecialistDelegation/v1`` (the delegation chain) and
``theforge/EvidenceHandoff/v1`` (the specialist→consumer evidence envelope)
natively, in the ``apiforge/*`` contract family.

Data-only rule: every field of a delegation record — findings, severities,
confidences, refs — is DATA about the producer's output. Nothing in it is an
instruction: there is no ``command``/``argv`` field a consumer could execute,
and the record never elevates authority (``severity``/``confidence`` are the
doctor's declared tokens, echoed verbatim — never normalized, never promoted).
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import Sha256

PROVIDER_ID = re.compile(r"^[a-z][a-z0-9-]{1,62}$")
CORRELATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

# Discovery lifecycle (audit G4): VERIFIED is a distinct state — a binary that
# answers `--version` with the doctor's identity — not merely "present".
DiscoveryState = Literal["absent", "untrusted", "verified"]

# Terminal states of the delegated run this record reports.
DelegationStatus = Literal["completed", "partial", "failed", "refused", "cancelled"]

# The named failure taxonomy, aligned to theforge DelegationFailure — a
# refusal/failure is always one of these codes, never an anonymous error.
DelegationFailure = Literal[
    "provider-absent",
    "version-incompatible",
    "invalid-input",
    "permission-denied",
    "timeout",
    "runtime-error",
    "invalid-output",
    "policy-refusal",
    "cycle-detected",
    "budget-exhausted",
    "cancelled",
]

MAX_VISITED_PROVIDERS = 32
MAX_DELEGATION_FINDINGS = 10_000


class DelegationChain(VersionedContract):
    """Chain-control state travelling with an in-flight delegation.

    Equivalent semantics to ``theforge/SpecialistDelegation/v1``'s chain
    block: ``visited_providers`` holds unique provider ids, the consumer that
    minted the chain is element 0 of a non-empty list, and the count is
    structural — ``len(visited) == delegation_depth + 1``. A revisit is a
    cycle refused at admission (``AF-DELEG-CYCLE``), never encoded.
    """

    correlation_id: str = ""
    delegation_depth: int = Field(default=0, ge=0)
    visited_providers: tuple[str, ...] = ()
    max_hops: int = Field(default=4, ge=1)
    timeout_budget_s: int = Field(default=600, gt=0)
    cancelled: bool = False

    @model_validator(mode="after")
    def _chain_invariants(self) -> DelegationChain:
        if self.correlation_id and not CORRELATION_ID.match(self.correlation_id):
            raise ValueError(f"invalid correlation_id {self.correlation_id!r}")
        if self.delegation_depth > self.max_hops:
            raise ValueError(
                f"delegation_depth {self.delegation_depth} exceeds max_hops {self.max_hops}"
            )
        if len(self.visited_providers) > MAX_VISITED_PROVIDERS:
            raise ValueError("visited_providers exceed bound")
        for provider in self.visited_providers:
            if not PROVIDER_ID.match(provider):
                raise ValueError(f"invalid visited provider id {provider!r}")
        if len(set(self.visited_providers)) != len(self.visited_providers):
            raise ValueError("visited_providers must be unique — a revisit is a cycle")
        if self.visited_providers:
            if len(self.visited_providers) != self.delegation_depth + 1:
                raise ValueError(
                    f"visited_providers ({len(self.visited_providers)}) must be "
                    f"delegation_depth + 1 ({self.delegation_depth + 1})"
                )
        elif self.delegation_depth > 0:
            raise ValueError("delegation_depth > 0 requires visited_providers")
        return self


class DoctorDiscovery(VersionedContract):
    """Measured presence of the forge-doctor-api CLI — never declared."""

    schema: Literal["apiforge/doctor-discovery/v1"] = "apiforge/doctor-discovery/v1"  # type: ignore[assignment]
    provider: str = "forge-doctor-api"
    state: DiscoveryState
    binary: str | None = None
    argv_prefix: tuple[str, ...] = ()
    cli_version: str | None = None
    package_version: str | None = None
    detail: str = ""


class DoctorFindingRow(VersionedContract):
    """One parsed ``id|sev|conf|subject[:line]|desc`` agent-format row.

    ``severity`` and ``confidence`` are the doctor's declared tokens echoed
    verbatim — a consumer treats them as data about the source's certainty,
    never as apiforge Severity/FindingStatus values.
    """

    check_id: str = Field(min_length=1)
    severity: str = Field(min_length=1)
    confidence: str = Field(min_length=1)
    subject: str = "-"
    line: int | None = Field(default=None, ge=1)
    description: str = ""


class DoctorUnknownRow(VersionedContract):
    """One ``UNKNOWN|subject|missing`` row — an explicit unresolvable."""

    subject: str = Field(min_length=1)
    missing: str = ""


class DoctorScan(VersionedContract):
    """A measured ``forge-doctor-api scan --format agent`` run and its parse."""

    schema: Literal["apiforge/doctor-scan/v1"] = "apiforge/doctor-scan/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    target: str = Field(min_length=1)
    argv: tuple[str, ...] = ()
    exit_code: int
    gate_failed: bool = False
    tool_version: str | None = None
    scan_schema_version: str | None = None
    knowledge_versions: dict[str, str] = Field(default_factory=dict)
    findings: tuple[DoctorFindingRow, ...] = ()
    unknowns: tuple[DoctorUnknownRow, ...] = ()
    stdout_sha256: Sha256
    stderr_tail: str = ""
    elapsed_ms: int = Field(default=0, ge=0)


class ScanDelta(VersionedContract):
    """Before/after comparison of two persisted doctor scans.

    ``delta_source`` is honest about who computed the delta: the doctor's own
    ``DeltaContext`` (``ApiHandoffBundle.delta`` via ``RequestDelta``) lives on
    its in-process ``DoctorBoundary``, not on the ``scan --format agent`` CLI —
    so this comparison is ``apiforge-derived`` over parsed findings keyed by
    (check_id, subject). It is a finding-set diff, never a claim that the
    doctor attested the delta itself.
    """

    baseline_ref: str = Field(min_length=1)
    current_ref: str = Field(min_length=1)
    delta_source: Literal["apiforge-derived", "doctor-delta"] = "apiforge-derived"
    findings_added: tuple[str, ...] = ()
    findings_removed: tuple[str, ...] = ()
    findings_changed: tuple[str, ...] = ()
    severity_changes: tuple[str, ...] = ()
    confidence_changes: tuple[str, ...] = ()
    unknowns_added: tuple[str, ...] = ()
    unknowns_removed: tuple[str, ...] = ()
    empty: bool = True


class DelegationErrorRecord(VersionedContract):
    """The named failure of a delegated run — never an anonymous error."""

    code: DelegationFailure
    detail: str = ""
    retryable: bool = False


class DoctorDelegationRecord(VersionedContract):
    """``apiforge/doctor-delegation/v1`` — the published evidence handoff.

    Field-for-field analogue of ``theforge/EvidenceHandoff/v1``: correlation
    and idempotency for dedup across a delegation chain, provider+version
    pairs on both ends, refs instead of payloads, findings with the
    producer's confidence verbatim, a named error state and an integrity
    binding (``integrity`` = sha256 of the canonical document with
    ``integrity=None``).
    """

    schema: Literal["apiforge/doctor-delegation/v1"] = "apiforge/doctor-delegation/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)
    source_provider: str = "forge-doctor-api"
    source_version: str = "unknown"
    consumer_provider: str = "api-forge"
    capability: str = "api.scan"
    status: DelegationStatus
    discovery_state: DiscoveryState | None = None
    input_refs: tuple[str, ...] = ()
    result_refs: tuple[str, ...] = ()
    findings: tuple[DoctorFindingRow, ...] = ()
    unknowns: tuple[DoctorUnknownRow, ...] = ()
    limitations: tuple[str, ...] = ()
    error: DelegationErrorRecord | None = None
    chain: DelegationChain = Field(default_factory=DelegationChain)
    delta: ScanDelta | None = None
    truncated: bool = False
    dropped: int = Field(default=0, ge=0)
    elapsed_ms: int = Field(default=0, ge=0)
    created_at: str = ""
    integrity: Sha256 | None = None

    @model_validator(mode="after")
    def _status_error_coherence(self) -> DoctorDelegationRecord:
        if self.status in ("failed", "refused", "cancelled") and self.error is None:
            raise ValueError(f"status {self.status!r} requires an error object")
        if self.status in ("completed", "partial") and self.error is not None:
            raise ValueError(f"status {self.status!r} must not carry an error object")
        if self.dropped > 0 and not self.truncated:
            raise ValueError("dropped > 0 requires truncated")
        for name in (self.run_id, self.correlation_id, self.idempotency_key):
            if not CORRELATION_ID.match(name):
                raise ValueError(f"invalid id {name!r}")
        return self


def record_integrity(record: DoctorDelegationRecord) -> str:
    """sha256 over the canonical record with ``integrity`` removed."""
    doc = record.model_dump(mode="json")
    doc["integrity"] = None
    canonical = json.dumps(doc, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = [
    "CORRELATION_ID",
    "PROVIDER_ID",
    "DelegationChain",
    "DelegationErrorRecord",
    "DelegationFailure",
    "DelegationStatus",
    "DiscoveryState",
    "DoctorDelegationRecord",
    "DoctorDiscovery",
    "DoctorFindingRow",
    "DoctorScan",
    "DoctorUnknownRow",
    "ScanDelta",
    "record_integrity",
]
