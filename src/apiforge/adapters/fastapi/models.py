"""Inventory produced by the static FastAPI extractor."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator

from apiforge.core.models import Diagnostic, Fact, JsonValue, freeze_json


class FastApiInventory(BaseModel):
    """Every route fact, diagnostic and source hash found under a project root."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    root: str
    facts: tuple[Fact, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    input_hashes: Mapping[str, str] = Field(default_factory=dict)

    @field_validator("input_hashes", mode="after")
    @classmethod
    def freeze_hashes(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("input_hashes must be a mapping")  # noqa: TRY004
        return frozen
