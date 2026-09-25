"""Deterministic path resolution independent of the current package checkout."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.distribution import ForgePaths as ForgePathsContract
from apiforge.contracts.distribution import PathSource


@dataclass(frozen=True, slots=True)
class ForgePaths:
    package_root: Path
    executable: Path
    state_root: Path
    config_path: Path | None
    cache_root: Path
    project_root: Path | None = None
    workspace_root: Path | None = None
    sources: tuple[tuple[str, PathSource], ...] = ()

    def contract(self) -> ForgePathsContract:
        return ForgePathsContract(
            package_root=str(self.package_root),
            executable=str(self.executable),
            state_root=str(self.state_root),
            config_path=str(self.config_path) if self.config_path else None,
            cache_root=str(self.cache_root),
            project_root=str(self.project_root) if self.project_root else None,
            workspace_root=str(self.workspace_root) if self.workspace_root else None,
            sources=self.sources,
        )


def _path(raw: str, *, cwd: Path, field: str) -> Path:
    value = raw.strip()
    if not value:
        raise ContractError("AF-DIST-PATH-INVALID", f"{field} cannot be empty")
    target = Path(value).expanduser()
    if not target.is_absolute():
        target = cwd / target
    try:
        return target.resolve()
    except OSError as exc:
        raise ContractError("AF-DIST-PATH-INVALID", f"{field} cannot be resolved: {exc}") from exc


def resolve_paths(
    *,
    cwd: Path | None = None,
    package_root: Path | None = None,
    env: Mapping[str, str] | None = None,
    project_root: Path | None = None,
    workspace_root: Path | None = None,
) -> ForgePaths:
    """Resolve package, user-owned state, config and cache paths.

    Environment overrides are explicit and never cause writes. Relative values
    are anchored to ``cwd`` so portable launchers behave consistently.
    """

    base = Path(cwd or Path.cwd()).resolve()
    values = env or os.environ
    package = Path(package_root or Path(__file__).resolve().parents[1]).resolve()
    sources: list[tuple[str, PathSource]] = [("package_root", "default")]

    project = project_root.resolve() if project_root else None
    workspace = workspace_root.resolve() if workspace_root else None
    home_raw = values.get("APIFORGE_HOME")
    if home_raw:
        state = _path(home_raw, cwd=base, field="APIFORGE_HOME")
        sources.append(("state_root", "environment"))
    else:
        state = (project or base) / ".apiforge"
        sources.append(("state_root", "default"))

    config_raw = values.get("APIFORGE_CONFIG")
    config = _path(config_raw, cwd=base, field="APIFORGE_CONFIG") if config_raw else None
    if config:
        sources.append(("config_path", "environment"))

    cache_raw = values.get("APIFORGE_CACHE")
    if cache_raw:
        cache = _path(cache_raw, cwd=base, field="APIFORGE_CACHE")
        sources.append(("cache_root", "environment"))
    else:
        cache = state / "cache"
        sources.append(("cache_root", "default"))

    executable = Path(sys.executable).resolve()
    return ForgePaths(
        package_root=package,
        executable=executable,
        state_root=state.resolve(),
        config_path=config,
        cache_root=cache.resolve(),
        project_root=project,
        workspace_root=workspace,
        sources=tuple(sources),
    )


__all__ = ["ForgePaths", "resolve_paths"]
