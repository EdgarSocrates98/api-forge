"""Read-only loader for packaged host templates and manifest metadata."""

from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from importlib.resources.abc import Traversable
from string import Template
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.core.yaml import StrictLoadError, load_yaml_mapping


def _resource(name: str) -> Traversable:
    target = files("apiforge.host_assets").joinpath(name)
    if not target.is_file():
        raise ContractError("AF-DIST-ASSET-MISSING", f"package asset {name!r} is missing")
    return target


def load_asset(name: str) -> tuple[str, str]:
    """Return UTF-8 asset content and its SHA-256 hash."""

    resource = _resource(name)
    try:
        content = resource.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ContractError("AF-DIST-ASSET-MISSING", f"asset {name!r} is unreadable") from exc
    return content, hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_manifest() -> dict[str, Any]:
    content, _ = load_asset("manifest.yaml")
    try:
        return dict(load_yaml_mapping(content, source="host_assets/manifest.yaml"))
    except (StrictLoadError, ValueError) as exc:
        raise ContractError(
            "AF-DIST-ASSET-MISSING", f"host asset manifest is invalid: {exc}"
        ) from exc


def render_template(name: str, values: dict[str, str]) -> tuple[str, str]:
    """Render a packaged template without writing to a consumer repository."""

    content, _ = load_asset(name)
    try:
        rendered = Template(content).substitute(values)
    except (KeyError, ValueError) as exc:
        raise ContractError("AF-HOST-TEMPLATE", f"template {name!r}: {exc}") from exc
    return rendered, hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def manifest_json() -> str:
    return json.dumps(load_manifest(), sort_keys=True, indent=2)


__all__ = ["load_asset", "load_manifest", "manifest_json", "render_template"]
