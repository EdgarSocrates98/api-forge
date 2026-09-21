"""Load the rule catalog shipped as package data."""

from __future__ import annotations

from collections.abc import Mapping
from importlib import resources
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from apiforge.core.models import Severity
from apiforge.core.yaml import StrictLoadError, load_yaml_strict

_CATALOG = "catalog/contract.yaml"


class CatalogError(ValueError):
    """A malformed rule catalog; ``str()`` begins with the code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


class RuleMeta(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str
    title: str
    severity: Severity
    rationale: str
    remediation: str
    reference: str = ""


def _parse(data: object, source: str) -> dict[str, RuleMeta]:
    if not isinstance(data, Mapping) or not isinstance(data.get("rules"), list):
        raise CatalogError("AF-CATALOG-SCHEMA", f"{source}: missing 'rules' list")
    catalog: dict[str, RuleMeta] = {}
    for index, entry in enumerate(data["rules"]):
        try:
            meta = RuleMeta(
                rule_id=entry["id"],
                title=entry["title"],
                severity=entry["severity"],
                rationale=entry.get("rationale", ""),
                remediation=entry.get("remediation", ""),
                reference=entry.get("reference", ""),
            )
        except Exception as exc:
            raise CatalogError(
                "AF-CATALOG-SCHEMA", f"{source}: rules[{index}] invalid: {exc}"
            ) from exc
        if meta.rule_id in catalog:
            raise CatalogError("AF-CATALOG-DUPLICATE", f"{source}: duplicate rule {meta.rule_id}")
        catalog[meta.rule_id] = meta
    return catalog


def load_catalog(path: Path | None = None) -> dict[str, RuleMeta]:
    """Return rule metadata keyed by rule id, from package data by default."""
    if path is None:
        text = resources.files("apiforge.rules").joinpath(_CATALOG).read_text(encoding="utf-8")
        source = "apiforge.rules catalog"
    else:
        text = Path(path).read_text(encoding="utf-8")
        source = str(path)
    try:
        data: Any = load_yaml_strict(text, source=source)
    except StrictLoadError as exc:
        raise CatalogError("AF-CATALOG-INVALID", str(exc)) from exc
    return _parse(data, source)
