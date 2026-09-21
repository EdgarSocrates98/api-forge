"""Manifest-last case persistence.

Artifacts are written first and `case.json` last, so a manifest never points
at an artifact that does not exist yet. Loading re-verifies every declared
hash. The output directory must not traverse upwards, hide behind a symlink,
or overlap the read-only inputs.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import ValidationError

import apiforge
from apiforge.case.models import ArtifactRef, CaseManifest, CasePayload
from apiforge.core.ids import stable_id
from apiforge.core.io import read_json, sha256_file, write_json


class CaseStorageError(ValueError):
    """A refused write; ``str()`` begins with the code."""

    def __init__(self, code: str, path: str) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code}: {path}")


class CaseIntegrityError(ValueError):
    """A tampered or incomplete case; ``str()`` begins with the code."""

    def __init__(self, code: str, path: str) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code}: {path}")


def _has_symlink_ancestor(path: Path) -> bool:
    current = Path(os.path.abspath(path))
    while True:
        if current.is_symlink():
            return True
        parent = current.parent
        if parent == current:
            return False
        current = parent


def _safe_out_dir(out_dir: Path) -> Path:
    raw = Path(out_dir)
    if ".." in raw.parts:
        raise CaseStorageError("AF-CASE-PATH-TRAVERSAL", str(raw))
    if _has_symlink_ancestor(raw):
        raise CaseStorageError("AF-CASE-SYMLINK", str(raw))
    return raw.resolve()


def _check_overlap(out: Path, payload: CasePayload) -> None:
    inputs = [
        Path(payload.contract_path).resolve(),
        Path(payload.project_path).resolve(),
    ]
    for source in inputs:
        if out == source or out.is_relative_to(source) or source.is_relative_to(out):
            raise CaseStorageError("AF-CASE-INPUT-OUTPUT-OVERLAP", str(source))


def _finding_counts(payload: CasePayload) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in payload.findings:
        counts[f"severity:{finding.severity}"] = counts.get(f"severity:{finding.severity}", 0) + 1
        counts[f"status:{finding.status}"] = counts.get(f"status:{finding.status}", 0) + 1
    return counts


def save_case(out_dir: Path, payload: CasePayload) -> CaseManifest:
    """Persist a case; the manifest is written last and returned."""
    out = _safe_out_dir(Path(out_dir))
    _check_overlap(out, payload)
    out.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, ArtifactRef] = {}
    planned: list[tuple[str, str, object]] = [
        ("api_ir", "api-ir.json", payload.model),
        ("facts", "facts.json", {"facts": list(payload.facts)}),
        ("findings", "findings.json", {"findings": list(payload.findings)}),
    ]
    if payload.changes:
        planned.append(("changes", "changes.json", {"changes": list(payload.changes)}))
    for name, filename, value in planned:
        write_json(out / filename, value)
        artifacts[name] = ArtifactRef(path=filename, sha256=sha256_file(out / filename))

    manifest = CaseManifest(
        generator=f"apiforge {apiforge.__version__}",
        case_id=stable_id(
            "case",
            {
                "inputs": {"contract": payload.contract_path, "project": payload.project_path},
                "input_hashes": dict(payload.model.input_hashes),
                "artifacts": {name: ref.sha256 for name, ref in artifacts.items()},
            },
        ),
        inputs={"contract": payload.contract_path, "project": payload.project_path},
        input_hashes=dict(payload.model.input_hashes),
        artifacts=artifacts,
        diagnostics_count=len(payload.diagnostics),
        finding_counts=_finding_counts(payload),
    )
    write_json(out / "case.json", manifest)
    return manifest


def _artifact_path(out: Path, ref: ArtifactRef) -> Path:
    rel = Path(ref.path)
    if rel.is_absolute() or ".." in rel.parts:
        raise CaseIntegrityError("AF-CASE-PATH-TRAVERSAL", ref.path)
    target = out / rel
    try:
        target.resolve().relative_to(out.resolve())
    except ValueError as exc:
        raise CaseIntegrityError("AF-CASE-PATH-TRAVERSAL", ref.path) from exc
    return target


def load_case(out_dir: Path) -> CaseManifest:
    """Load a case manifest and verify every declared artifact hash."""
    out = Path(out_dir)
    manifest_path = out / "case.json"
    if not manifest_path.is_file():
        raise CaseIntegrityError("AF-CASE-MANIFEST-MISSING", str(manifest_path))
    try:
        data: Any = read_json(manifest_path)
        manifest = CaseManifest(**data)
    except (ValidationError, TypeError) as exc:
        raise CaseIntegrityError("AF-CASE-INVALID", str(manifest_path)) from exc
    for name in sorted(manifest.artifacts):
        ref = manifest.artifacts[name]
        target = _artifact_path(out, ref)
        if not target.is_file():
            raise CaseIntegrityError("AF-CASE-ARTIFACT-MISSING", ref.path)
        if sha256_file(target) != ref.sha256:
            raise CaseIntegrityError("AF-CASE-HASH-MISMATCH", ref.path)
    return manifest
