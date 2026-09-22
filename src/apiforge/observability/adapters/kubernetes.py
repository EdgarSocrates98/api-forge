"""Kubernetes metadata adapter for local manifests."""

from pathlib import Path


def discover(path: Path) -> dict[str, object]:
    return {"path": str(path), "read_only": True, "resources": sorted(item.name for item in path.glob("**/*.yaml")) if path.is_dir() else []}
