"""First-wave deterministic configuration precedence."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.core.yaml import StrictLoadError, load_yaml_mapping

DEFAULT_CONFIG: dict[str, Any] = {
    "scope": {"default": "repo"},
    "evidence": {"strict": True},
    "host": {"activation": {"mode": "plan_only"}},
    "network": {"mode": "offline_first"},
    "workspace": {"discover_parent": True},
    "assets": {"verify_hashes": True},
}
_SECRET_KEYS = ("secret", "token", "password", "credential", "api_key", "private_key")


def _merge(base: dict[str, Any], extra: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in extra.items():
        if any(part in str(key).lower() for part in _SECRET_KEYS):
            raise ContractError("AF-MANIFEST-SECRET", f"secret-like key {key!r} is not allowed")
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _merge(dict(result[key]), value)
        else:
            result[key] = value
    return result


def _load(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    try:
        value = load_yaml_mapping(path.read_text(encoding="utf-8"), source=str(path))
    except (OSError, UnicodeDecodeError, StrictLoadError) as exc:
        raise ContractError("AF-MANIFEST-INVALID", f"{path}: {exc}") from exc
    return dict(value)


def resolve_config(
    *,
    paths: Any,
    workspace_path: Path | None = None,
    project_path: Path | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge defaults → user config → workspace → project → CLI overrides."""

    result = _merge({}, DEFAULT_CONFIG)
    result = _merge(result, _load(paths.config_path))
    result = _merge(result, _load(workspace_path))
    result = _merge(result, _load(project_path))
    if overrides:
        result = _merge(result, overrides)
    return result


__all__ = ["DEFAULT_CONFIG", "resolve_config"]
