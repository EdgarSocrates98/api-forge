"""Receipt models. Frozen; serializable; no implicit wall-clock data."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)


class ReceiptArtifact(_Frozen):
    path: str
    sha256: str
    kind: str


class Receipt(_Frozen):
    schema_version: str = "af-receipt/1"
    proves: str = (
        "correspondence between the listed paths and their sha256 contents at "
        "emit time; it does not prove authorship or freshness"
    )
    case: str
    policy_sha256: str
    artifacts: tuple[ReceiptArtifact, ...]
    input_hashes: tuple[tuple[str, str], ...] = ()
    emitted_at: str | None = None
