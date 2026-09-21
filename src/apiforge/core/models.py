"""Immutable contracts shared by API Forge analysis stages."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from enum import StrEnum
from math import isfinite
from typing import Annotated, Any, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    StringConstraints,
    field_validator,
    model_validator,
)

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | tuple[JsonValue, ...] | Mapping[str, JsonValue]


class FrozenJsonMap(dict[str, JsonValue]):
    """A JSON object with normal mapping behavior and no mutation methods."""

    def __setitem__(self, key: str, value: JsonValue) -> None:
        raise TypeError("JSON payloads are immutable")

    def __delitem__(self, key: str) -> None:
        raise TypeError("JSON payloads are immutable")

    def clear(self) -> None:
        raise TypeError("JSON payloads are immutable")

    def pop(self, key: str, default: Any = None) -> JsonValue:
        raise TypeError("JSON payloads are immutable")

    def popitem(self) -> tuple[str, JsonValue]:
        raise TypeError("JSON payloads are immutable")

    def setdefault(  # type: ignore[override]
        self, key: str, default: JsonValue = None
    ) -> JsonValue:
        raise TypeError("JSON payloads are immutable")

    def update(  # type: ignore[override]
        self,
        other: Mapping[str, JsonValue] | Iterable[tuple[str, JsonValue]] = (),
        **kwargs: JsonValue,
    ) -> None:
        raise TypeError("JSON payloads are immutable")

    def __ior__(  # type: ignore[override,misc]
        self, other: Mapping[str, JsonValue] | Iterable[tuple[str, JsonValue]]
    ) -> Self:
        raise TypeError("JSON payloads are immutable")


def freeze_json(value: object) -> JsonValue:
    if value is None or isinstance(value, str | bool | int):
        return value
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError("JSON payloads cannot contain NaN or Infinity")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, JsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")  # noqa: TRY004
            frozen[key] = freeze_json(item)
        return FrozenJsonMap(frozen)
    if isinstance(value, list | tuple):
        return tuple(freeze_json(item) for item in value)
    raise ValueError(f"value of type {type(value).__name__} is not JSON-compatible")


class _ContractModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class FindingStatus(StrEnum):
    CONFIRMED = "confirmed"
    UNRESOLVED = "unresolved"
    NOT_APPLICABLE = "not_applicable"


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class SourceRef(_ContractModel):
    """Location and content identity for extracted evidence."""

    path: str
    sha256: Sha256
    line: PositiveInt | None = None
    column: PositiveInt | None = None
    extractor: str = "apiforge"


class Fact(_ContractModel):
    version: Literal[1] = 1
    fact_id: str
    kind: str
    source: SourceRef
    measures: Mapping[str, JsonValue] = Field(default_factory=FrozenJsonMap)
    attrs: Mapping[str, JsonValue] = Field(default_factory=FrozenJsonMap)

    @field_validator("measures", "attrs", mode="after")
    @classmethod
    def freeze_payload(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("JSON payload must be an object")  # noqa: TRY004
        return frozen


class Finding(_ContractModel):
    version: Literal[1] = 1
    finding_id: str
    rule_id: str
    status: FindingStatus
    severity: Severity
    title: str
    detail: str = ""
    evidence: tuple[str, ...] = ()
    remediation: str | None = None

    @model_validator(mode="after")
    def require_confirmed_evidence(self) -> Finding:
        if self.status is FindingStatus.CONFIRMED and not self.evidence:
            raise ValueError("confirmed findings require evidence")
        return self


class Diagnostic(_ContractModel):
    code: str
    status: FindingStatus
    message: str
    source: SourceRef | None = None
    details: Mapping[str, JsonValue] = Field(default_factory=FrozenJsonMap)

    @field_validator("details", mode="after")
    @classmethod
    def freeze_details(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("diagnostic details must be a JSON object")  # noqa: TRY004
        return frozen
