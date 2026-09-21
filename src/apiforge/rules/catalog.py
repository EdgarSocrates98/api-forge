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
    "check",
}

_CHECK_KEYS = {"kind", "path", "op", "value"}
_CHECK_OPS = {"gt", "ge", "lt", "le", "eq", "ne", "present"}


class RuleCheck(BaseModel):
    """Closed executable predicate over a fact kind — thresholds stay data."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: str
    path: str  # dotted path into measures/attrs
    op: str
    value: object = None


def _parse_check(raw: object, source: str, rule_id: str) -> RuleCheck | None:
    if raw is None:
        return None
    if not isinstance(raw, Mapping) or not set(raw) <= _CHECK_KEYS:
        raise CatalogError(
            "AF-CATALOG-SCHEMA", f"{source}: {rule_id} check must map {_CHECK_KEYS}"
        )
    if raw.get("op") not in _CHECK_OPS or not isinstance(raw.get("kind"), str):
        raise CatalogError(
            "AF-CATALOG-SCHEMA",
            f"{source}: {rule_id} check needs kind + op in {sorted(_CHECK_OPS)}",
        )
    if not isinstance(raw.get("path"), str):
        raise CatalogError("AF-CATALOG-SCHEMA", f"{source}: {rule_id} check needs path")
    return RuleCheck(
        kind=raw["kind"], path=raw["path"], op=raw["op"], value=raw.get("value")
    )


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
    check: RuleCheck | None = None


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
                check=_parse_check(entry.get("check"), source, str(entry["id"])),
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


def load_playbooks() -> dict[str, tuple[dict[str, str], ...]]:
    """Executor decomposition per coordinator, from package data.

    Each value is the ordered tuple of steps ``{executor, verb, purpose}``.
    """
    text = (
        resources.files("apiforge.rules")
        .joinpath("playbooks.yaml")
        .read_text(encoding="utf-8")
    )
    try:
        data: Any = load_yaml_strict(text, source="playbooks.yaml")
    except StrictLoadError as exc:
        raise CatalogError("AF-CATALOG-INVALID", str(exc)) from exc
    if not isinstance(data, Mapping):
        raise CatalogError("AF-CATALOG-INVALID", "playbooks.yaml is not a mapping")
    out: dict[str, tuple[dict[str, str], ...]] = {}
    for name, steps in data.items():
        if not isinstance(steps, list):
            raise CatalogError("AF-CATALOG-INVALID", f"playbook {name!r} is not a list")
        parsed: list[dict[str, str]] = []
        for step in steps:
            if not isinstance(step, Mapping) or set(step) != {
                "executor",
                "verb",
                "purpose",
            }:
                raise CatalogError(
                    "AF-CATALOG-INVALID", f"playbook {name!r} has a malformed step"
                )
            parsed.append({k: str(step[k]) for k in ("executor", "verb", "purpose")})
        out[str(name)] = tuple(parsed)
    return out
