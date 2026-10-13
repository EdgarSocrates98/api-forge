"""Language-neutral inventory contract shared by every adapter."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator

from apiforge.contracts.adapter import AdapterExecution
from apiforge.core.models import Diagnostic, Fact, JsonValue, freeze_json


class CodeInventory(BaseModel):
    """Route facts, diagnostics and source hashes for one framework.

    `facts` carry kind `code.route` with `measures.method`/`measures.path`;
    `input_hashes` covers every file the extractor scanned, parsed or not.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    framework: str
    root: str
    facts: tuple[Fact, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    input_hashes: Mapping[str, str] = Field(default_factory=dict)
    execution: AdapterExecution | None = None

    @field_validator("input_hashes", mode="after")
    @classmethod
    def freeze_hashes(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("input_hashes must be a mapping")  # noqa: TRY004
        return frozen


def static_execution(
    adapter_id: str,
    input_hashes: Mapping[str, str],
    diagnostics: tuple[Diagnostic, ...] = (),
    *,
    limitations: tuple[str, ...] = (),
) -> AdapterExecution:
    """Build the common provenance envelope for static source adapters."""

    return AdapterExecution(
        adapter_id=adapter_id,
        adapter_version="static-v1",
        mode="static",
        status="partial" if diagnostics else "completed",
        evidence_level="heuristic",
        input_hashes=tuple(sorted((str(key), str(value)) for key, value in input_hashes.items())),
        tools=("filesystem-read",),
        evidence_refs=tuple(
            f"source:{key}#{value[:16]}" for key, value in sorted(input_hashes.items())
        ),
        unresolved=tuple(sorted(diagnostic.code for diagnostic in diagnostics)),
        limitations=limitations,
    )
