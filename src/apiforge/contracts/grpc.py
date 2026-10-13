"""Versioned, provider-neutral contracts for the gRPC control plane."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract


class GrpcStreamMode(StrEnum):
    UNARY = "unary"
    CLIENT = "client_streaming"
    SERVER = "server_streaming"
    BIDI = "bidirectional_streaming"


class GrpcSeverity(StrEnum):
    INFO = "info"
    REVIEW = "review"
    BREAKING = "breaking"


class GrpcField(VersionedContract):
    name: str
    number: int = Field(ge=1)
    type_name: str
    label: Literal["optional", "required", "repeated"] = "optional"
    json_name: str | None = None
    reserved: bool = False


class GrpcMessage(VersionedContract):
    name: str
    full_name: str
    fields: tuple[GrpcField, ...] = ()
    reserved_numbers: tuple[int, ...] = ()
    reserved_names: tuple[str, ...] = ()


class GrpcRpc(VersionedContract):
    name: str
    full_name: str
    request_type: str
    response_type: str
    stream_mode: GrpcStreamMode = GrpcStreamMode.UNARY
    idempotent: bool = False
    http_method: str | None = None
    http_path: str | None = None
    source_path: str | None = None
    source_line: int | None = None


class GrpcService(VersionedContract):
    name: str
    full_name: str
    rpcs: tuple[GrpcRpc, ...] = ()


class GrpcIR(VersionedContract):
    package: str = ""
    source_path: str
    source_sha256: str
    imports: tuple[str, ...] = ()
    messages: tuple[GrpcMessage, ...] = ()
    services: tuple[GrpcService, ...] = ()
    enums: tuple[str, ...] = ()
    enum_values: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    unresolved: tuple[str, ...] = ()
    descriptor_sha256: str | None = None
    provenance: tuple[str, ...] = ()


class GrpcDiagnostic(VersionedContract):
    code: str
    severity: GrpcSeverity
    message: str
    path: str | None = None
    evidence: tuple[str, ...] = ()


class GrpcCompatibilityReport(VersionedContract):
    baseline_digest: str
    candidate_digest: str
    verdict: Literal["compatible", "review", "breaking", "inconclusive"]
    diagnostics: tuple[GrpcDiagnostic, ...] = ()


class GrpcCapability(VersionedContract):
    name: str
    available: bool
    tool_version: str | None = None
    mode: Literal["read_only", "local_reversible", "external_mutation"] = "read_only"
    reason: str | None = None


class GrpcCodegenRequest(VersionedContract):
    languages: tuple[Literal["python", "go", "java"], ...] = ("python",)
    output_dir: str = "generated"
    tool: Literal["fake", "protoc", "buf"] = "fake"


class GrpcArtifact(VersionedContract):
    path: str
    sha256: str
    language: str
    generated: bool = True


class GrpcCodegenResult(VersionedContract):
    status: Literal["generated", "unsupported", "blocked", "failed"]
    artifacts: tuple[GrpcArtifact, ...] = ()
    capabilities: tuple[GrpcCapability, ...] = ()
    diagnostics: tuple[GrpcDiagnostic, ...] = ()


class GrpcGatewayRequest(VersionedContract):
    gateways: tuple[Literal["envoy", "grpc_gateway", "grpc_web", "openapi"], ...] = ("openapi",)
    output_dir: str = "gateway"


class GrpcGatewayProjection(VersionedContract):
    gateway: str
    status: Literal["projected", "unsupported", "blocked"]
    artifacts: tuple[GrpcArtifact, ...] = ()
    diagnostics: tuple[GrpcDiagnostic, ...] = ()


class GrpcRuntimePolicy(VersionedContract):
    deadline_ms: int = Field(default=5000, ge=1)
    max_attempts: int = Field(default=1, ge=1, le=10)
    max_message_bytes: int = Field(default=4194304, ge=1)
    max_stream_duration_s: int = Field(default=3600, ge=1)
    health_check: bool = True
    reflection: bool = False
    allow_non_idempotent_retry: bool = False


class GrpcPerformanceRun(VersionedContract):
    requests: int = Field(ge=0)
    duration_s: float = Field(gt=0)
    concurrency: int = Field(ge=1)
    latency_p50_ms: float | None = Field(default=None, ge=0)
    latency_p95_ms: float | None = Field(default=None, ge=0)
    latency_p99_ms: float | None = Field(default=None, ge=0)
    stream_messages: int | None = Field(default=None, ge=0)
    generator_saturation: float | None = Field(default=None, ge=0, le=1)


class GrpcPerformanceReport(VersionedContract):
    rps: float
    tps: float | None
    valid: bool
    reason: str | None = None


class GrpcSecurityReport(VersionedContract):
    safe: bool
    redacted_fields: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()


class GrpcPlan(VersionedContract):
    intention: str
    phases: tuple[str, ...]
    risk: Literal["low", "medium", "high", "critical"]
    requires_review: bool
    proof_axes: tuple[str, ...]
    metadata: dict[str, Any] = Field(default_factory=dict)


class GrpcVerification(VersionedContract):
    verdict: Literal["DONE", "REVIEW", "BLOCKED"]
    checks: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
