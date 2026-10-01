"""Policy models: a closed vocabulary for autonomy decisions."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from apiforge.core.models import JsonValue, freeze_json


class AutonomyClass(StrEnum):
    """Spec §11 classes, ordered from least to most dangerous."""

    READ_ONLY = "read_only"
    LOCAL_REVERSIBLE = "local_reversible"
    SENSITIVE = "sensitive"
    EXTERNAL_MUTATION = "external_mutation"
    DESTRUCTIVE = "destructive"
    IRREVERSIBLE = "irreversible"


Decision = Literal["allow", "gate", "deny"]

#: Closed vocabulary of gate requirement names.
KNOWN_REQUIREMENTS = frozenset(
    {
        "exact_target",
        "impact",
        "dry_run_or_reason",
        "rollback",
        "confirmation",
        "evidence",
        "approval",
        "identity_resolved",
        "backup",
    }
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class RuleMatch(_Frozen):
    verb: str
    arg_glob: str | None = None


class PolicyRule(_Frozen):
    name: str
    match: RuleMatch
    decision: Decision
    reason: str | None = None


class Policy(_Frozen):
    version: Literal[1] = 1
    defaults: Mapping[AutonomyClass, Decision] = Field(default_factory=dict)
    gates: Mapping[AutonomyClass, tuple[str, ...]] = Field(default_factory=dict)
    rules: tuple[PolicyRule, ...] = ()

    @field_validator("defaults", "gates", mode="after")
    @classmethod
    def freeze_maps(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("policy fields must be mappings")  # noqa: TRY004
        return frozen
