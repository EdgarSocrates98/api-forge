"""Content-addressed generated artifact helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path

from apiforge.contracts.grpc import GrpcArtifact


def artifact(path: Path, language: str) -> GrpcArtifact:
    return GrpcArtifact(
        path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), language=language
    )


def verify(path: Path, expected_sha256: str) -> bool:
    return path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha256
