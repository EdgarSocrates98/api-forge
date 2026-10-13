"""Read-only discovery coordinator for runtime migrations."""

from __future__ import annotations

import hashlib
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.migration.adapters import ADAPTERS
from apiforge.migration.contracts import DiscoveryResult, MigrationSpec
from apiforge.migration.matrix import resolve_versions


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover(spec: MigrationSpec, matrix_path: Path | None = None) -> DiscoveryResult:
    root = Path(spec.project_root).resolve()
    if not root.is_dir():
        raise ContractError("AF-MIGRATION-ROOT", f"project root is not a directory: {root}")
    resolve_versions(spec.ecosystem, spec.source_version, spec.target_version, matrix_path)
    adapter = next((item for item in ADAPTERS if item.ecosystem == spec.ecosystem), None)
    if adapter is None or not adapter.can_handle(spec.source_version, spec.target_version):
        raise ContractError("AF-MIGRATION-ADAPTER", f"no adapter for {spec.identity()}")
    observation = adapter.discover(root, spec.source_version, spec.target_version)
    hashes = tuple(
        (path, _hash(root / path)) for path in observation.files if (root / path).is_file()
    )
    return DiscoveryResult(
        spec_identity=spec.identity(),
        ecosystem=spec.ecosystem,
        detected_files=observation.files,
        capabilities=observation.capabilities,
        findings=observation.findings,
        input_hashes=hashes,
    )
