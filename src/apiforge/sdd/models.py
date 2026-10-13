"""SDD models: canonical phases, artifacts, discovery, and profiles."""

from __future__ import annotations

from collections.abc import Mapping
from importlib import resources
from pathlib import Path
from types import MappingProxyType

from pydantic import BaseModel, ConfigDict, Field, field_validator

from apiforge.core.models import JsonValue, freeze_json
from apiforge.core.yaml import load_yaml_mapping

PHASES = (
    "discover",
    "intent",
    "contract",
    "architecture",
    "plan",
    "build",
    "verify",
    "secure",
    "benchmark",
    "ship",
)

PHASE_STATUS = frozenset({"draft", "ready", "done", "superseded", "not_required"})


class SddError(ValueError):
    """A refused SDD operation; ``str()`` begins with the code."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SddArtifact(_Frozen):
    """A phase artifact: parsed frontmatter meta plus body, or an error."""

    path: Path
    meta: Mapping[str, JsonValue] = Field(default_factory=dict)
    body: str = ""
    error: str | None = None

    @field_validator("meta", mode="after")
    @classmethod
    def freeze_meta(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("artifact meta must be a mapping")  # noqa: TRY004
        return frozen


class SkippedEntry(_Frozen):
    """A directory entry that is not a feature — reported, never dropped."""

    name: str
    reason: str


class FeatureDiscovery(_Frozen):
    """Everything under an SDD root: feature dirs and named skips."""

    root: Path
    features: Mapping[str, Mapping[str, Path]] = Field(default_factory=dict)
    skipped: tuple[SkippedEntry, ...] = ()

    @field_validator("features", mode="after")
    @classmethod
    def freeze_features(
        cls, value: Mapping[str, Mapping[str, Path]]
    ) -> Mapping[str, Mapping[str, Path]]:
        return MappingProxyType(
            {name: MappingProxyType(dict(phases)) for name, phases in value.items()}
        )


class StampResult(_Frozen):
    path: str
    upstream: str
    sha256: str
    previous: str | None = None
    changed: bool


class SddIssue(_Frozen):
    """A named refusal or gap — code, location, field, and what unlocks it."""

    code: str
    feature: str
    message: str
    phase: str | None = None
    field: str | None = None
    unlock: str | None = None


class SddReport(_Frozen):
    ok: bool
    root: str
    features: tuple[str, ...]
    refused: tuple[SddIssue, ...] = ()
    unresolved: tuple[SddIssue, ...] = ()


class SddStatus(_Frozen):
    root: str
    features: Mapping[str, JsonValue] = Field(default_factory=dict)

    @field_validator("features", mode="after")
    @classmethod
    def freeze_map(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("features must be a mapping")  # noqa: TRY004
        return frozen


class PhaseChange(_Frozen):
    feature: str
    phase: str
    previous: str | None
    status: str
    overrides_applied: tuple[str, ...] = ()
    changed: bool


class Gate(_Frozen):
    name: str
    satisfied_by: str
    produced_by: str
    guards_phases: tuple[str, ...]


def load_profiles() -> Mapping[str, tuple[str, ...]]:
    """Load profile → required phases from package data."""
    text = resources.files("apiforge.sdd").joinpath("profiles.yaml").read_text(encoding="utf-8")
    data = load_yaml_mapping(text, source="apiforge.sdd profiles")
    raw = data.get("profiles")
    if not isinstance(raw, Mapping):
        raise SddError("AF-SDD-PROFILES", "profiles.yaml missing 'profiles' mapping")
    profiles: dict[str, tuple[str, ...]] = {}
    for name, phases in raw.items():
        if not isinstance(phases, list):
            raise SddError("AF-SDD-PROFILES", f"profiles.{name} must be a list")
        unknown = [p for p in phases if p not in PHASES]
        if unknown:
            raise SddError("AF-SDD-PROFILES", f"profiles.{name}: unknown phase {unknown[0]!r}")
        profiles[str(name)] = tuple(str(p) for p in phases)
    missing = {"quick", "standard", "critical", "migration"} - set(profiles)
    if missing:
        raise SddError("AF-SDD-PROFILES", f"profiles missing: {sorted(missing)}")
    return profiles


def load_gates() -> tuple[Gate, ...]:
    """Load the gate catalog from package data."""
    text = resources.files("apiforge.sdd").joinpath("gates.yaml").read_text(encoding="utf-8")
    data = load_yaml_mapping(text, source="apiforge.sdd gates")
    raw = data.get("gates")
    if not isinstance(raw, Mapping):
        raise SddError("AF-SDD-GATES", "gates.yaml missing 'gates' mapping")
    gates: list[Gate] = []
    for name, entry in raw.items():
        if not isinstance(entry, Mapping):
            raise SddError("AF-SDD-GATES", f"gates.{name} must be a mapping")
        try:
            gates.append(
                Gate(
                    name=str(name),
                    satisfied_by=str(entry["satisfied_by"]),
                    produced_by=str(entry["produced_by"]),
                    guards_phases=tuple(str(p) for p in entry["guards_phases"]),
                )
            )
        except (KeyError, TypeError) as exc:
            raise SddError("AF-SDD-GATES", f"gates.{name}: {exc}") from exc
    return tuple(gates)
