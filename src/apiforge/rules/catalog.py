"""Load the multi-area rule catalog shipped as package data.

Every ``catalog/*.yaml`` file declares ``area`` and ``rules[]`` under a
closed schema — unknown keys, ``expected_gain`` and duplicate rule ids are
refused, never ignored.
"""

from __future__ import annotations

from collections.abc import Mapping
from importlib import resources
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from apiforge.core.models import Severity
from apiforge.core.yaml import StrictLoadError, load_yaml_strict

_CATALOG_DIR = "catalog"

_RULE_KEYS = {
    "id",
    "title",
    "severity",
    "rationale",
    "remediation",
    "reference",
    "runtime_scope",
}


class CatalogError(ValueError):
    """A malformed rule catalog; ``str()`` begins with the code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


class RuleMeta(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str
    area: str
    title: str
    severity: Severity
    rationale: str
    remediation: str
    reference: str = ""
    runtime_scope: str | None = None


def _merge(target: dict[str, RuleMeta], parsed: dict[str, RuleMeta], source: str) -> None:
    for rule_id, meta in parsed.items():
        if rule_id in target:
            raise CatalogError("AF-CATALOG-DUPLICATE-RULE", f"{source}: duplicate rule {rule_id}")
        target[rule_id] = meta


def _parse(data: object, source: str) -> dict[str, RuleMeta]:
    if not isinstance(data, Mapping):
        raise CatalogError("AF-CATALOG-SCHEMA", f"{source}: not a mapping")
    area = data.get("area")
    if not isinstance(area, str) or not area:
        raise CatalogError("AF-CATALOG-AREA-MISSING", f"{source}: missing 'area'")
    if not isinstance(data.get("rules"), list):
        raise CatalogError("AF-CATALOG-SCHEMA", f"{source}: missing 'rules' list")
    catalog: dict[str, RuleMeta] = {}
    for index, entry in enumerate(data["rules"]):
        if not isinstance(entry, Mapping):
            raise CatalogError("AF-CATALOG-SCHEMA", f"{source}: rules[{index}] not a mapping")
        unknown = set(entry) - _RULE_KEYS
        if unknown:
            raise CatalogError(
                "AF-CATALOG-SCHEMA",
                f"{source}: rules[{index}] unknown keys {sorted(unknown)}",
            )
        try:
            meta = RuleMeta(
                rule_id=entry["id"],
                area=area,
                title=entry["title"],
                severity=entry["severity"],
                rationale=entry.get("rationale", ""),
                remediation=entry.get("remediation", ""),
                reference=entry.get("reference", ""),
                runtime_scope=entry.get("runtime_scope"),
            )
        except Exception as exc:
            raise CatalogError(
                "AF-CATALOG-SCHEMA", f"{source}: rules[{index}] invalid: {exc}"
            ) from exc
        _merge(catalog, {meta.rule_id: meta}, source)
    return catalog


def _parse_text(text: str, source: str) -> dict[str, RuleMeta]:
    try:
        data: Any = load_yaml_strict(text, source=source)
    except StrictLoadError as exc:
        raise CatalogError("AF-CATALOG-INVALID", str(exc)) from exc
    return _parse(data, source)


def load_catalog_text(text: str, *, source: str = "<catalog>") -> dict[str, RuleMeta]:
    """Parse a single catalog document from a string."""
    return _parse_text(text, source)


def _catalog_dir() -> Any:
    return resources.files("apiforge.rules").joinpath(_CATALOG_DIR)


def _documents(path: Path | None) -> list[tuple[str, str]]:
    """Return (source, text) pairs in deterministic order."""
    if path is None:
        entries = sorted(_catalog_dir().iterdir(), key=lambda e: str(e))
        return [
            (str(e), e.read_text(encoding="utf-8"))
            for e in entries
            if str(e).endswith(".yaml") and not str(e).endswith("routing.yaml")
        ]
    path = Path(path)
    if path.is_dir():
        return [
            (str(p), p.read_text(encoding="utf-8"))
            for p in sorted(path.glob("*.yaml"))
            if p.name != "routing.yaml"
        ]
    return [(str(path), path.read_text(encoding="utf-8"))]


def load_catalog(path: Path | None = None) -> dict[str, RuleMeta]:
    """Return rule metadata keyed by rule id, from package data by default.

    ``path`` may point at a single catalog file or a directory of them.
    """
    catalog: dict[str, RuleMeta] = {}
    for source, text in _documents(path):
        _merge(catalog, _parse_text(text, source), source)
    return catalog


def load_areas(path: Path | None = None) -> tuple[str, ...]:
    """Sorted unique rule areas declared across catalog files."""
    areas: set[str] = set()
    for source, text in _documents(path):
        try:
            data: Any = load_yaml_strict(text, source=source)
        except StrictLoadError as exc:
            raise CatalogError("AF-CATALOG-INVALID", str(exc)) from exc
        if isinstance(data, Mapping) and isinstance(data.get("area"), str):
            areas.add(data["area"])
    return tuple(sorted(areas))
