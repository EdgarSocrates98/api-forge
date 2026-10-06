"""Offline-first runtime migration control plane."""

from apiforge.migration.contracts import (
    DiscoveryResult,
    MigrationFinding,
    MigrationReport,
    MigrationSpec,
)
from apiforge.migration.discovery import discover
from apiforge.migration.matrix import (
    compatibility_matrix,
    load_matrix,
    observe_python_interpreter,
    resolve_versions,
)
from apiforge.migration.planner import compile_plan
from apiforge.migration.verifier import verify_report

__all__ = [
    "DiscoveryResult",
    "MigrationFinding",
    "MigrationReport",
    "MigrationSpec",
    "compatibility_matrix",
    "compile_plan",
    "discover",
    "load_matrix",
    "observe_python_interpreter",
    "resolve_versions",
    "verify_report",
]
