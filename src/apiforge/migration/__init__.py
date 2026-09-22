"""Offline-first runtime migration control plane."""

from apiforge.migration.contracts import (
    DiscoveryResult,
    MigrationFinding,
    MigrationReport,
    MigrationSpec,
)
from apiforge.migration.discovery import discover
from apiforge.migration.matrix import load_matrix, resolve_versions
from apiforge.migration.planner import compile_plan
from apiforge.migration.verifier import verify_report

__all__ = [
    "DiscoveryResult",
    "MigrationFinding",
    "MigrationReport",
    "MigrationSpec",
    "compile_plan",
    "discover",
    "load_matrix",
    "resolve_versions",
    "verify_report",
]
