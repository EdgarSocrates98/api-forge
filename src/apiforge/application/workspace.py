"""Canonical workspace application facade."""

from __future__ import annotations

from pathlib import Path

from apiforge.workspace.service import WorkspaceService


def discover(root: Path | None = None) -> object:
    return WorkspaceService(root).discovery()


def initialize(root: Path | None = None, *, name: str | None = None) -> object:
    return WorkspaceService(root).init(workspace=True, name=name)


def add(root: Path, repository: Path) -> object:
    return WorkspaceService(root).add(repository)


def status(root: Path | None = None) -> object:
    return WorkspaceService(root).status()


__all__ = ["add", "discover", "initialize", "status"]
