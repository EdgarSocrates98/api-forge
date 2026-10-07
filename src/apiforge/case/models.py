"""Case persistence models: the payload in, the manifest out."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator

from apiforge.api_ir.models import ApiModel
from apiforge.core.models import (
    Diagnostic,
    Fact,
    Finding,
    JsonValue,
    Sha256,
    freeze_json,
)
from apiforge.openapi.diff import ContractChange


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class CasePayload(_Frozen):
    """Everything an analysis produced, before persistence."""

    contract_path: str
    project_path: str
    model: ApiModel
    facts: tuple[Fact, ...] = ()
    findings: tuple[Finding, ...] = ()
    changes: tuple[ContractChange, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()


class ArtifactRef(_Frozen):
    path: str
    sha256: Sha256


class CaseManifest(_Frozen):
    """Manifest written last; every declared artifact is hashed."""

    schema_version: str = "1"
    generator: str
    case_id: str
    inputs: Mapping[str, str] = Field(default_factory=dict)
    input_hashes: Mapping[str, str] = Field(default_factory=dict)
    artifacts: Mapping[str, ArtifactRef] = Field(default_factory=dict)
    diagnostics_count: int = 0
    finding_counts: Mapping[str, int] = Field(default_factory=dict)

    @field_validator("inputs", "input_hashes", "finding_counts", mode="after")
    @classmethod
    def freeze_maps(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("manifest fields must be mappings")  # noqa: TRY004
        return frozen
