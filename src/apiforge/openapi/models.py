"""Normalized, provenance-backed view of an OpenAPI 3.1 document."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator

from apiforge.core.models import Diagnostic, JsonValue, Sha256, SourceRef, freeze_json


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class OpenApiOperation(_Frozen):
    """One contract operation, keyed by lowercase method and verbatim path."""

    method: str
    path: str
    operation_id: str | None = None
    source: SourceRef
    raw: Mapping[str, JsonValue] = Field(default_factory=dict)
    fact_id: str

    @field_validator("raw", mode="after")
    @classmethod
    def freeze_raw(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("operation payload must be an object")  # noqa: TRY004
        return frozen


class OpenApiDocument(_Frozen):
    """A loaded contract: operations sorted by path then method, raw components kept."""

    version: str
    source_path: str
    sha256: Sha256
    operations: tuple[OpenApiOperation, ...] = ()
    components: Mapping[str, JsonValue] = Field(default_factory=dict)
    diagnostics: tuple[Diagnostic, ...] = ()

    @field_validator("components", mode="after")
    @classmethod
    def freeze_components(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("components must be an object")  # noqa: TRY004
        return frozen
