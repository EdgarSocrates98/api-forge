"""The API-IR: one operation keyed by method+path, every projection kept."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator

from apiforge.core.models import Diagnostic, JsonValue, SourceRef, freeze_json


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Projection(_Frozen):
    """One observation of an operation from a single source."""

    source_kind: str  # "contract" | "code"
    fact_id: str
    source: SourceRef
    detail: Mapping[str, JsonValue] = Field(default_factory=dict)

    @field_validator("detail", mode="after")
    @classmethod
    def freeze_detail(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("projection detail must be an object")  # noqa: TRY004
        return frozen


class ApiOperation(_Frozen):
    """A canonical operation; contract and code projections may both be absent."""

    method: str
    path: str
    contract_projections: tuple[Projection, ...] = ()
    code_projections: tuple[Projection, ...] = ()

    @property
    def contract(self) -> Projection | None:
        """The first contract projection, or None when the contract lacks it."""
        return self.contract_projections[0] if self.contract_projections else None


class ApiModel(_Frozen):
    """The canonical API model: operations plus provenance and diagnostics."""

    schema_version: str = "1"
    generator: str
    input_hashes: Mapping[str, str] = Field(default_factory=dict)
    operations: tuple[ApiOperation, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()

    @field_validator("input_hashes", mode="after")
    @classmethod
    def freeze_hashes(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("input_hashes must be a mapping")  # noqa: TRY004
        return frozen

    def operation(self, method: str, path: str) -> ApiOperation:
        """Return the operation for `method`/`path`, raising KeyError if absent."""
        key = (method.lower(), path)
        for operation in self.operations:
            if (operation.method, operation.path) == key:
                return operation
        raise KeyError(f"{method.upper()} {path}")
